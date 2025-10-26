import math

DEADZONE = 0.35

def calculate_pose_similarity(landmarks1, landmarks2):
    """
    Calculate similarity between two poses based on landmark distances.
    Returns a score from 0-100, where 100 is a perfect match.
    """
    if landmarks1 is None or landmarks2 is None:
        return 0.0
    
    total_distance = 0.0
    num_landmarks = len(landmarks1.landmark)
    
    for i in range(num_landmarks):
        lm1 = landmarks1.landmark[i]
        lm2 = landmarks2.landmark[i]
        
        # Calculate Euclidean distance between corresponding landmarks
        distance = math.sqrt(
            (lm1.x - lm2.x) ** 2 + 
            (lm1.y - lm2.y) ** 2 + 
            (lm1.z - lm2.z) ** 2
        )
        distance -= DEADZONE
        distance = max(0, distance)
        total_distance += distance
    
    # Average distance per landmark
    avg_distance = total_distance / num_landmarks
    # avg_distance = min(0.2, avg_distance)


    # Convert to similarity score (0-100)
    # Assuming max reasonable distance is 1.0 (full diagonal of normalized space)
    similarity = max(0, 100 - (avg_distance * 100))
    
    return similarity


def calculate_pose_similarity_wo_face(landmarks1, landmarks2):
    """
    Calculate similarity between two poses based on landmark distances.
    Returns a score from 0-100, where 100 is a perfect match.
    Excludes face landmarks (0-10) to focus on body pose.
    """
    if landmarks1 is None or landmarks2 is None:
        return 0.0
    
    # Exclude face landmarks (indices 0-10: nose, eyes, ears, mouth)
    # Start from index 11 (left shoulder) onwards
    body_landmark_start = 11
    
    total_distance = 0.0
    num_landmarks = 0
    
    for i in range(body_landmark_start, len(landmarks1.landmark)):
        lm1 = landmarks1.landmark[i]
        lm2 = landmarks2.landmark[i]
        
        # Calculate Euclidean distance between corresponding landmarks
        distance = math.sqrt(
            (lm1.x - lm2.x) ** 2 + 
            (lm1.y - lm2.y) ** 2 + 
            (lm1.z - lm2.z) ** 2
        )
        total_distance += distance
        num_landmarks += 1
    
    # Average distance per landmark
    avg_distance = total_distance / num_landmarks
    
    # Convert to similarity score (0-100)
    # Assuming max reasonable distance is 1.0 (full diagonal of normalized space)
    similarity = max(0, 100 - (avg_distance * 100))
    
    return similarity


def calculate_alignment(landmarks_source, landmarks_target):
    """
    Calculate the optimal x/y offset and scale to align source landmarks to target landmarks.
    Returns: (offset_x, offset_y, scale)
    
    Uses body landmarks only (excludes face landmarks 0-10).
    """
    if landmarks_source is None or landmarks_target is None:
        return 0.0, 0.0, 1.0
    
    body_landmark_start = 11
    
    # Calculate centroids (average position) of both poses
    source_x, source_y = 0.0, 0.0
    target_x, target_y = 0.0, 0.0
    num_landmarks = 0
    
    for i in range(body_landmark_start, len(landmarks_source.landmark)):
        source_x += landmarks_source.landmark[i].x
        source_y += landmarks_source.landmark[i].y
        target_x += landmarks_target.landmark[i].x
        target_y += landmarks_target.landmark[i].y
        num_landmarks += 1
    
    source_x /= num_landmarks
    source_y /= num_landmarks
    target_x /= num_landmarks
    target_y /= num_landmarks
    
    # Calculate scale based on average distance from centroid
    source_scale = 0.0
    target_scale = 0.0
    
    for i in range(body_landmark_start, len(landmarks_source.landmark)):
        source_lm = landmarks_source.landmark[i]
        target_lm = landmarks_target.landmark[i]
        
        source_dist = math.sqrt((source_lm.x - source_x) ** 2 + (source_lm.y - source_y) ** 2)
        target_dist = math.sqrt((target_lm.x - target_x) ** 2 + (target_lm.y - target_y) ** 2)
        
        source_scale += source_dist
        target_scale += target_dist
    
    source_scale /= num_landmarks
    target_scale /= num_landmarks
    
    # Calculate scale factor
    if source_scale > 0:
        scale = target_scale / source_scale
    else:
        scale = 1.0
    
    # Calculate offset (after scaling from center point 0.5, 0.5)
    # Transform source centroid with scale, then calculate offset to target centroid
    scaled_source_x = (source_x - 0.5) * scale + 0.5
    scaled_source_y = (source_y - 0.5) * scale + 0.5
    
    offset_x = target_x - scaled_source_x
    offset_y = target_y - scaled_source_y
    
    return offset_x, offset_y, scale