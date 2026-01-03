import AuditLog from '../models/AuditLog.model.js';

export const auditLog = (action, resource) => {
  return async (req, res, next) => {
    // Store original json method
    const originalJson = res.json.bind(res);

    // Override json method to capture response
    res.json = function(data) {
      // Log audit entry after successful operation
      if (res.statusCode >= 200 && res.statusCode < 300 && req.user) {
        const resourceId = req.params.id || req.body.id || data.data?._id || data.data?.id;
        
        AuditLog.create({
          user: req.user._id,
          action,
          resource,
          resourceId,
          changes: req.method !== 'GET' ? req.body : undefined,
          ipAddress: req.ip || req.connection.remoteAddress,
          userAgent: req.get('user-agent')
        }).catch(err => {
          console.error('Audit log error:', err);
        });
      }

      // Call original json method
      return originalJson(data);
    };

    next();
  };
};





