import Report from '../models/Report.model.js';
import Alert from '../models/Alert.model.js';
import Camera from '../models/Camera.model.js';
import Snapshot from '../models/Snapshot.model.js';
import PDFDocument from 'pdfkit';
import createCsvWriter from 'csv-writer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const getAllReports = async (req, res) => {
  try {
    const { page = 1, limit = 10 } = req.query;

    const query = {};
    
    // Non-admin users can only see their own reports
    if (req.user.role !== 'admin') {
      query.generatedBy = req.user._id;
    }

    const reports = await Report.find(query)
      .populate('generatedBy', 'name email')
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const total = await Report.countDocuments(query);

    res.json({
      success: true,
      data: {
        reports,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch reports',
      error: error.message
    });
  }
};

export const getReportById = async (req, res) => {
  try {
    const report = await Report.findById(req.params.id)
      .populate('generatedBy', 'name email');

    if (!report) {
      return res.status(404).json({
        success: false,
        message: 'Report not found'
      });
    }

    // Non-admin users can only see their own reports
    if (req.user.role !== 'admin' && report.generatedBy._id.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to view this report'
      });
    }

    res.json({
      success: true,
      data: { report }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch report',
      error: error.message
    });
  }
};

export const generateReport = async (req, res) => {
  try {
    const { type, dateRange, filters, format = 'pdf' } = req.body;

    if (!type || !dateRange || !dateRange.start || !dateRange.end) {
      return res.status(400).json({
        success: false,
        message: 'Type and date range are required'
      });
    }

    // Create report record
    const report = await Report.create({
      title: `${type.charAt(0).toUpperCase() + type.slice(1)} Report - ${new Date(dateRange.start).toLocaleDateString()} to ${new Date(dateRange.end).toLocaleDateString()}`,
      type,
      generatedBy: req.user._id,
      dateRange: {
        start: new Date(dateRange.start),
        end: new Date(dateRange.end)
      },
      filters: filters || {},
      format,
      status: 'generating'
    });

    // Generate report asynchronously
    generateReportFile(report, type, dateRange, filters, format)
      .then(async (fileInfo) => {
        report.fileUrl = fileInfo.fileUrl;
        report.fileSize = fileInfo.fileSize;
        report.status = 'completed';
        report.metadata = {
          totalRecords: fileInfo.totalRecords,
          generatedAt: new Date()
        };
        await report.save();
      })
      .catch(async (error) => {
        console.error('Report generation error:', error);
        report.status = 'failed';
        await report.save();
      });

    res.status(201).json({
      success: true,
      message: 'Report generation started',
      data: { report }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to generate report',
      error: error.message
    });
  }
};

async function generateReportFile(report, type, dateRange, filters, format) {
  const uploadsDir = path.join(__dirname, '../uploads/reports');
  await fs.mkdir(uploadsDir, { recursive: true });

  const startDate = new Date(dateRange.start);
  const endDate = new Date(dateRange.end);

  let data = [];
  let totalRecords = 0;

  if (type === 'alerts') {
    const query = {
      detectedAt: {
        $gte: startDate,
        $lte: endDate
      }
    };

    if (filters?.cameras?.length) query.camera = { $in: filters.cameras };
    if (filters?.alertTypes?.length) query.type = { $in: filters.alertTypes };
    if (filters?.severities?.length) query.severity = { $in: filters.severities };
    if (filters?.statuses?.length) query.status = { $in: filters.statuses };

    const alerts = await Alert.find(query)
      .populate('camera', 'name location')
      .sort({ detectedAt: -1 });

    totalRecords = alerts.length;
    data = alerts.map(alert => ({
      id: alert._id,
      camera: alert.camera?.name || 'N/A',
      location: alert.camera?.location || 'N/A',
      type: alert.type,
      severity: alert.severity,
      status: alert.status,
      detectedAt: alert.detectedAt.toISOString(),
      description: alert.description || ''
    }));
  } else if (type === 'cameras') {
    const cameras = await Camera.find(filters?.cameras ? { _id: { $in: filters.cameras } } : {})
      .sort({ createdAt: -1 });

    totalRecords = cameras.length;
    data = cameras.map(camera => ({
      id: camera._id,
      name: camera.name,
      location: camera.location,
      ipAddress: camera.ipAddress,
      status: camera.status,
      isActive: camera.isActive,
      aiEnabled: camera.aiEnabled,
      createdAt: camera.createdAt.toISOString()
    }));
  } else if (type === 'snapshots') {
    const query = {
      capturedAt: {
        $gte: startDate,
        $lte: endDate
      }
    };

    if (filters?.cameras?.length) query.camera = { $in: filters.cameras };

    const snapshots = await Snapshot.find(query)
      .populate('camera', 'name location')
      .sort({ capturedAt: -1 });

    totalRecords = snapshots.length;
    data = snapshots.map(snapshot => ({
      id: snapshot._id,
      camera: snapshot.camera?.name || 'N/A',
      location: snapshot.camera?.location || 'N/A',
      capturedAt: snapshot.capturedAt.toISOString(),
      tags: snapshot.tags?.join(', ') || ''
    }));
  }

  const filename = `report-${report._id}-${Date.now()}.${format}`;
  const filePath = path.join(uploadsDir, filename);

  if (format === 'pdf') {
    await generatePDF(data, filePath, report.title, type);
  } else {
    await generateCSV(data, filePath);
  }

  const stats = await fs.stat(filePath);

  return {
    fileUrl: `/uploads/reports/${filename}`,
    fileSize: stats.size,
    totalRecords
  };
}

async function generatePDF(data, filePath, title, type) {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument();
    const stream = fs.createWriteStream(filePath);
    doc.pipe(stream);

    doc.fontSize(20).text(title, { align: 'center' });
    doc.moveDown();
    doc.fontSize(12).text(`Generated: ${new Date().toLocaleString()}`);
    doc.moveDown();
    doc.fontSize(12).text(`Total Records: ${data.length}`);
    doc.moveDown(2);

    if (data.length > 0) {
      const headers = Object.keys(data[0]);
      doc.fontSize(10).font('Helvetica-Bold');
      headers.forEach((header, i) => {
        doc.text(header.charAt(0).toUpperCase() + header.slice(1), 50, doc.y, { width: 100 });
      });
      doc.moveDown();

      doc.font('Helvetica').fontSize(8);
      data.forEach((row, index) => {
        if (index > 0 && index % 30 === 0) {
          doc.addPage();
        }
        headers.forEach(header => {
          doc.text(String(row[header] || ''), 50, doc.y, { width: 100 });
        });
        doc.moveDown(0.5);
      });
    }

    doc.end();
    stream.on('finish', resolve);
    stream.on('error', reject);
  });
}

async function generateCSV(data, filePath) {
  if (data.length === 0) {
    await fs.writeFile(filePath, '');
    return;
  }

  const headers = Object.keys(data[0]).map(key => ({
    id: key,
    title: key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')
  }));

  const csvWriter = createCsvWriter.createObjectCsvWriter({
    path: filePath,
    header: headers
  });

  await csvWriter.writeRecords(data);
}

export const downloadReport = async (req, res) => {
  try {
    const report = await Report.findById(req.params.id);

    if (!report) {
      return res.status(404).json({
        success: false,
        message: 'Report not found'
      });
    }

    if (report.status !== 'completed' || !report.fileUrl) {
      return res.status(400).json({
        success: false,
        message: 'Report is not ready for download'
      });
    }

    // Non-admin users can only download their own reports
    if (req.user.role !== 'admin' && report.generatedBy.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Not authorized to download this report'
      });
    }

    const filePath = path.join(__dirname, '..', report.fileUrl);
    
    try {
      await fs.access(filePath);
      const filename = `report-${report._id}.${report.format}`;
      res.download(filePath, filename);
    } catch (error) {
      res.status(404).json({
        success: false,
        message: 'Report file not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to download report',
      error: error.message
    });
  }
};





