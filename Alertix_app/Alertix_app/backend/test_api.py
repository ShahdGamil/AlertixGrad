"""
Test script for Alertix YOLO Theft Detection API
=================================================
This script tests the API endpoints to ensure everything is working correctly.

Usage:
    python test_api.py

Requirements:
    pip install requests pillow numpy
"""

import os
import sys
import json
import base64
from io import BytesIO
from datetime import datetime

try:
    import requests
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Install with: pip install requests pillow numpy")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message):
    """Print an info message."""
    print(f"ℹ {message}")


def create_test_image(width=640, height=640):
    """
    Create a simple test image if no real image is available.

    Returns:
        BytesIO: Image in memory
    """
    # Create a colored test image
    image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

    # Add some text
    from PIL import ImageDraw, ImageFont

    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    # Draw text
    draw.text((width // 2 - 50, height // 2), "TEST IMAGE", fill=(255, 255, 255))

    # Save to bytes
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG')
    buffer.seek(0)

    return buffer


def save_base64_image(base64_string, output_path="output_detection.jpg"):
    """
    Save a base64 encoded image to file.

    Args:
        base64_string: Base64 encoded image string
        output_path: Path to save the image
    """
    try:
        # Decode base64
        image_data = base64.b64decode(base64_string)

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(image_data)

        print_success(f"Detection image saved to: {output_path}")
        return True
    except Exception as e:
        print_error(f"Failed to save image: {str(e)}")
        return False

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_health_check():
    """Test the /health endpoint."""
    print_section("Test 1: Health Check")

    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_success("Health check successful!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Model loaded: {data.get('model_loaded')}")
            print_info(f"API version: {data.get('api_version')}")
            print_info(f"Timestamp: {data.get('timestamp')}")
            return True
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API server at {API_BASE_URL}")
        print_info("Make sure the server is running with: python backend.py")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def test_prediction_with_test_image():
    """Test the /predict endpoint with a generated test image."""
    print_section("Test 2: Prediction with Test Image")

    try:
        # Create test image
        print_info("Creating test image...")
        test_image = create_test_image()

        # Prepare request
        files = {
            'image': ('test_image.jpg', test_image, 'image/jpeg')
        }

        data = {
            'camera_id': 'test_camera_001',
            'camera_name': 'Test Camera',
            'confidence_threshold': 0.25,
            'include_image': True
        }

        print_info("Sending prediction request...")
        response = requests.post(PREDICT_ENDPOINT, files=files, data=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print_success("Prediction successful!")
            print_info(f"Theft detected: {result.get('theft_detected')}")
            print_info(f"Total detections: {result.get('total_detections')}")
            print_info(f"Overall confidence: {result.get('overall_confidence', 0.0):.2f}")
            print_info(f"Description: {result.get('description')}")

            # Print detections
            if result.get('detections'):
                print("\nDetections:")
                for idx, detection in enumerate(result['detections'], 1):
                    print(f"  {idx}. Class: {detection['class_name']}, "
                          f"Confidence: {detection['confidence']:.2f}, "
                          f"BBox: {detection['bbox']}")

            # Save image with boxes if available
            if result.get('image_with_boxes'):
                print_info("Saving detection image...")
                save_base64_image(result['image_with_boxes'], "test_output_detection.jpg")

            return True
        else:
            print_error(f"Prediction failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Prediction test failed: {str(e)}")
        return False


def test_prediction_with_real_image(image_path):
    """Test the /predict endpoint with a real image file."""
    print_section(f"Test 3: Prediction with Real Image ({image_path})")

    if not os.path.exists(image_path):
        print_error(f"Image file not found: {image_path}")
        return False

    try:
        # Open image file
        with open(image_path, 'rb') as f:
            files = {
                'image': (os.path.basename(image_path), f, 'image/jpeg')
            }

            data = {
                'camera_id': 'real_camera_001',
                'camera_name': 'Real Camera Test',
                'confidence_threshold': 0.25,
                'include_image': True
            }

            print_info("Sending prediction request...")
            response = requests.post(PREDICT_ENDPOINT, files=files, data=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print_success("Prediction successful!")
            print_info(f"Theft detected: {result.get('theft_detected')}")
            print_info(f"Total detections: {result.get('total_detections')}")
            print_info(f"Overall confidence: {result.get('overall_confidence', 0.0):.2f}")
            print_info(f"Description: {result.get('description')}")

            # Print detections
            if result.get('detections'):
                print("\nDetections:")
                for idx, detection in enumerate(result['detections'], 1):
                    print(f"  {idx}. Class: {detection['class_name']}, "
                          f"Confidence: {detection['confidence']:.2f}, "
                          f"BBox: {detection['bbox']}")

            # Save image with boxes if available
            if result.get('image_with_boxes'):
                output_path = f"real_output_{os.path.basename(image_path)}"
                print_info("Saving detection image...")
                save_base64_image(result['image_with_boxes'], output_path)

            return True
        else:
            print_error(f"Prediction failed with status code: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Prediction test failed: {str(e)}")
        return False


def test_api_documentation():
    """Test if API documentation is accessible."""
    print_section("Test 4: API Documentation")

    docs_url = f"{API_BASE_URL}/docs"
    redoc_url = f"{API_BASE_URL}/redoc"

    try:
        # Test Swagger UI
        response = requests.get(docs_url, timeout=10)
        if response.status_code == 200:
            print_success(f"Swagger UI accessible at: {docs_url}")
        else:
            print_error(f"Swagger UI not accessible")

        # Test ReDoc
        response = requests.get(redoc_url, timeout=10)
        if response.status_code == 200:
            print_success(f"ReDoc accessible at: {redoc_url}")
        else:
            print_error(f"ReDoc not accessible")

        return True
    except Exception as e:
        print_error(f"Documentation test failed: {str(e)}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all API tests."""
    print("\n" + "=" * 70)
    print("  ALERTIX YOLO THEFT DETECTION API - TEST SUITE")
    print("=" * 70)
    print(f"  API URL: {API_BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = []

    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))

    # Test 2: Prediction with test image
    results.append(("Test Image Prediction", test_prediction_with_test_image()))

    # Test 3: Prediction with real image (if available)
    # Look for any image files in current directory
    image_files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if image_files:
        test_image_path = image_files[0]
        results.append(("Real Image Prediction", test_prediction_with_real_image(test_image_path)))
    else:
        print_section("Test 3: Real Image Prediction")
        print_info("No image files found in current directory. Skipping real image test.")
        print_info("To test with a real image, place a .jpg or .png file in this directory.")

    # Test 4: API Documentation
    results.append(("API Documentation", test_api_documentation()))

    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {test_name}: {status}")

    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print_success("All tests passed! Your API is working correctly.")
        print_info("You can now connect your Flutter app to this backend.")
    else:
        print_error(f"{total - passed} test(s) failed. Please check the errors above.")

    print("\nNext steps:")
    print("  1. Check the Swagger UI: http://localhost:8000/docs")
    print("  2. Update your Flutter app API URL")
    print("  3. Test from your Flutter app")
    print()


if __name__ == "__main__":
    main()
