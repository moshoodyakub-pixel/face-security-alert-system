"""
Image Processing Utility Module
Helper functions for image preprocessing, face alignment, quality checks, and format conversions.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


def resize_image(
    image: np.ndarray,
    target_size: Tuple[int, int],
    maintain_aspect_ratio: bool = True
) -> np.ndarray:
    """
    Resize image to target size.
    
    Args:
        image (np.ndarray): Input image
        target_size (tuple): Target size (width, height)
        maintain_aspect_ratio (bool): If True, maintains aspect ratio with padding
    
    Returns:
        np.ndarray: Resized image
    """
    if image is None or image.size == 0:
        logger.error("Invalid input image for resizing")
        return image
    
    target_width, target_height = target_size
    
    if not maintain_aspect_ratio:
        # Simple resize
        resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized
    
    # Resize maintaining aspect ratio
    height, width = image.shape[:2]
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height
    
    if aspect_ratio > target_aspect_ratio:
        # Width is limiting factor
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # Height is limiting factor
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Create canvas and paste resized image
    if len(image.shape) == 3:
        canvas = np.zeros((target_height, target_width, image.shape[2]), dtype=image.dtype)
    else:
        canvas = np.zeros((target_height, target_width), dtype=image.dtype)
    
    # Calculate padding
    y_offset = (target_height - new_height) // 2
    x_offset = (target_width - new_width) // 2
    
    # Place resized image on canvas
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
    
    return canvas


def normalize_image(image: np.ndarray, method: str = "standard") -> np.ndarray:
    """
    Normalize image pixel values.
    
    Args:
        image (np.ndarray): Input image
        method (str): Normalization method ('standard', 'minmax', 'meanstd')
    
    Returns:
        np.ndarray: Normalized image
    """
    if image is None or image.size == 0:
        logger.error("Invalid input image for normalization")
        return image
    
    # Convert to float
    img_float = image.astype(np.float32)
    
    if method == "standard":
        # Normalize to [0, 1]
        normalized = img_float / 255.0
        
    elif method == "minmax":
        # Min-max normalization
        min_val = np.min(img_float)
        max_val = np.max(img_float)
        
        if max_val > min_val:
            normalized = (img_float - min_val) / (max_val - min_val)
        else:
            normalized = img_float
            
    elif method == "meanstd":
        # Mean-std normalization
        mean = np.mean(img_float)
        std = np.std(img_float)
        
        if std > 0:
            normalized = (img_float - mean) / std
        else:
            normalized = img_float - mean
            
    else:
        logger.warning(f"Unknown normalization method: {method}, using standard")
        normalized = img_float / 255.0
    
    return normalized


def check_image_quality(image: np.ndarray) -> dict:
    """
    Check image quality metrics.
    
    Args:
        image (np.ndarray): Input image
    
    Returns:
        dict: Quality metrics including brightness, contrast, sharpness, etc.
    """
    if image is None or image.size == 0:
        return {
            'valid': False,
            'error': 'Invalid image'
        }
    
    quality_metrics = {'valid': True}
    
    try:
        # Convert to grayscale for analysis
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Brightness (mean pixel value)
        brightness = np.mean(gray)
        quality_metrics['brightness'] = float(brightness)
        
        # Check if too dark or too bright
        if brightness < 50:
            quality_metrics['brightness_issue'] = 'too_dark'
        elif brightness > 200:
            quality_metrics['brightness_issue'] = 'too_bright'
        else:
            quality_metrics['brightness_issue'] = None
        
        # Contrast (standard deviation)
        contrast = np.std(gray)
        quality_metrics['contrast'] = float(contrast)
        
        if contrast < 20:
            quality_metrics['contrast_issue'] = 'too_low'
        else:
            quality_metrics['contrast_issue'] = None
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        quality_metrics['sharpness'] = float(sharpness)
        
        if sharpness < 100:
            quality_metrics['sharpness_issue'] = 'blurry'
        else:
            quality_metrics['sharpness_issue'] = None
        
        # Overall quality score (0-100)
        brightness_score = 100 - abs(brightness - 127) / 127 * 100
        contrast_score = min(contrast / 50 * 100, 100)
        sharpness_score = min(sharpness / 500 * 100, 100)
        
        quality_metrics['overall_score'] = (
            brightness_score * 0.3 +
            contrast_score * 0.3 +
            sharpness_score * 0.4
        )
        
        logger.debug(f"Image quality: {quality_metrics['overall_score']:.1f}")
        
    except Exception as e:
        logger.error(f"Error checking image quality: {e}")
        quality_metrics['valid'] = False
        quality_metrics['error'] = str(e)
    
    return quality_metrics


def align_face(
    image: np.ndarray,
    left_eye: Optional[Tuple[int, int]] = None,
    right_eye: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """
    Align face based on eye positions.
    
    Args:
        image (np.ndarray): Input face image
        left_eye (tuple): Coordinates of left eye (x, y)
        right_eye (tuple): Coordinates of right eye (x, y)
    
    Returns:
        np.ndarray: Aligned face image
    """
    if image is None or image.size == 0:
        logger.error("Invalid input image for alignment")
        return image
    
    if left_eye is None or right_eye is None:
        logger.debug("Eye positions not provided, skipping alignment")
        return image
    
    try:
        # Calculate angle between eyes
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Calculate center point between eyes
        eye_center = (
            (left_eye[0] + right_eye[0]) // 2,
            (left_eye[1] + right_eye[1]) // 2
        )
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(eye_center, angle, scale=1.0)
        
        # Apply rotation
        aligned = cv2.warpAffine(
            image,
            rotation_matrix,
            (image.shape[1], image.shape[0]),
            flags=cv2.INTER_CUBIC
        )
        
        logger.debug(f"Face aligned with rotation angle: {angle:.2f}°")
        return aligned
        
    except Exception as e:
        logger.error(f"Error aligning face: {e}")
        return image


def convert_color_space(
    image: np.ndarray,
    source: str = "BGR",
    target: str = "RGB"
) -> np.ndarray:
    """
    Convert image between color spaces.
    
    Args:
        image (np.ndarray): Input image
        source (str): Source color space (BGR, RGB, GRAY, HSV)
        target (str): Target color space (BGR, RGB, GRAY, HSV)
    
    Returns:
        np.ndarray: Converted image
    """
    if image is None or image.size == 0:
        logger.error("Invalid input image for color space conversion")
        return image
    
    if source == target:
        return image
    
    conversion_map = {
        ('BGR', 'RGB'): cv2.COLOR_BGR2RGB,
        ('RGB', 'BGR'): cv2.COLOR_RGB2BGR,
        ('BGR', 'GRAY'): cv2.COLOR_BGR2GRAY,
        ('RGB', 'GRAY'): cv2.COLOR_RGB2GRAY,
        ('BGR', 'HSV'): cv2.COLOR_BGR2HSV,
        ('RGB', 'HSV'): cv2.COLOR_RGB2HSV,
        ('HSV', 'BGR'): cv2.COLOR_HSV2BGR,
        ('HSV', 'RGB'): cv2.COLOR_HSV2RGB,
        ('GRAY', 'BGR'): cv2.COLOR_GRAY2BGR,
        ('GRAY', 'RGB'): cv2.COLOR_GRAY2RGB,
    }
    
    conversion_code = conversion_map.get((source.upper(), target.upper()))
    
    if conversion_code is None:
        logger.warning(f"Conversion from {source} to {target} not supported")
        return image
    
    try:
        converted = cv2.cvtColor(image, conversion_code)
        return converted
    except Exception as e:
        logger.error(f"Error converting color space: {e}")
        return image


def enhance_image(image: np.ndarray, method: str = "clahe") -> np.ndarray:
    """
    Enhance image quality using various methods.
    
    Args:
        image (np.ndarray): Input image
        method (str): Enhancement method ('clahe', 'histogram', 'brightness')
    
    Returns:
        np.ndarray: Enhanced image
    """
    if image is None or image.size == 0:
        logger.error("Invalid input image for enhancement")
        return image
    
    try:
        if method == "clahe":
            # Contrast Limited Adaptive Histogram Equalization
            if len(image.shape) == 3:
                # Convert to LAB color space
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Apply CLAHE to L channel
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l_enhanced = clahe.apply(l)
                
                # Merge channels and convert back
                enhanced_lab = cv2.merge([l_enhanced, a, b])
                enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            else:
                # Grayscale image
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(image)
        
        elif method == "histogram":
            # Histogram equalization
            if len(image.shape) == 3:
                # Convert to YCrCb
                ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
                channels = cv2.split(ycrcb)
                channels[0] = cv2.equalizeHist(channels[0])
                ycrcb_enhanced = cv2.merge(channels)
                enhanced = cv2.cvtColor(ycrcb_enhanced, cv2.COLOR_YCrCb2BGR)
            else:
                enhanced = cv2.equalizeHist(image)
        
        elif method == "brightness":
            # Simple brightness adjustment
            enhanced = cv2.convertScaleAbs(image, alpha=1.2, beta=20)
        
        else:
            logger.warning(f"Unknown enhancement method: {method}")
            enhanced = image
        
        logger.debug(f"Image enhanced using method: {method}")
        return enhanced
        
    except Exception as e:
        logger.error(f"Error enhancing image: {e}")
        return image


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with a sample image
    print("Image Processing Utilities Test")
    print("=" * 50)
    
    # Create a test image
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Test resize
    print("\n1. Testing resize...")
    resized = resize_image(test_image, (320, 240), maintain_aspect_ratio=True)
    print(f"Original size: {test_image.shape}, Resized: {resized.shape}")
    
    # Test normalization
    print("\n2. Testing normalization...")
    normalized = normalize_image(test_image, method="standard")
    print(f"Normalized range: [{normalized.min():.3f}, {normalized.max():.3f}]")
    
    # Test quality check
    print("\n3. Testing quality check...")
    quality = check_image_quality(test_image)
    print(f"Quality score: {quality.get('overall_score', 0):.1f}")
    
    # Test color conversion
    print("\n4. Testing color conversion...")
    rgb_image = convert_color_space(test_image, "BGR", "RGB")
    print(f"Converted to RGB: {rgb_image.shape}")
    
    print("\nAll tests completed!")
