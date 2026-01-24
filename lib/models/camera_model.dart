import 'package:flutter/foundation.dart';
import 'package:hive/hive.dart';

part 'camera_model.g.dart';

@immutable
@HiveType(typeId: 3)
class CameraModel {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String name;

  @HiveField(2)
  final String location;

  @HiveField(3)
  final String? cameraNumber;

  @HiveField(4)
  final DateTime createdAt;

  @HiveField(5)
  final bool isActive;

  const CameraModel({
    required this.id,
    required this.name,
    required this.location,
    required this.createdAt,
    this.cameraNumber,
    this.isActive = true,
  });

  factory CameraModel.fromJson(Map<String, dynamic> json) {
    return CameraModel(
      id: json['id'] as String,
      name: json['name'] as String,
      location: json['location'] as String,
      cameraNumber: json['camera_number'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      isActive: json['is_active'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'location': location,
      'camera_number': cameraNumber,
      'created_at': createdAt.toIso8601String(),
      'is_active': isActive,
    };
  }

  CameraModel copyWith({
    String? id,
    String? name,
    String? location,
    String? cameraNumber,
    DateTime? createdAt,
    bool? isActive,
  }) {
    return CameraModel(
      id: id ?? this.id,
      name: name ?? this.name,
      location: location ?? this.location,
      cameraNumber: cameraNumber ?? this.cameraNumber,
      createdAt: createdAt ?? this.createdAt,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  String toString() {
    return 'CameraModel(id: $id, name: $name, location: $location, cameraNumber: $cameraNumber, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is CameraModel && other.id == id;
  }

  @override
  int get hashCode {
    return id.hashCode;
  }
}
