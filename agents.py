"""
Multi-Agent Natural Language Communication System
Based on: "Multi-agent Communication meets Natural Language"

This module implements speaker and listener agents that communicate
using natural language, combining functional learning (RL-based) and
structural learning (language model-based).
"""

import random
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


@dataclass
class Image:
    """Represents an image with attributes."""
    id: int
    color: str
    shape: str
    size: str
    position: str
    
    def __repr__(self) -> str:
        return f"Image({self.id}: {self.color} {self.size} {self.shape} at {self.position})"


class ImageEnvironment:
    """Creates and manages image dataset for communication task."""
    
    COLORS = ["red", "blue", "green", "yellow", "purple"]
    SHAPES = ["circle", "square", "triangle", "pentagon", "star"]
    SIZES = ["tiny", "small", "medium", "large", "huge"]
    POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
    
    def __init__(self, dataset_size: int = 50):
        """Initialize environment with dataset of images."""
        self.dataset = self._generate_images(dataset_size)
        self.current_target = None
        
    def _generate_images(self, size: int) -> List[Image]:
        """Generate diverse images with unique combinations."""
        images = []
        for i in range(size):
            image = Image(
                id=i,
                color=random.choice(self.COLORS),
                shape=random.choice(self.SHAPES),
                size=random.choice(self.SIZES),
                position=random.choice(self.POSITIONS)
            )
            images.append(image)
        return images
    
    def get_candidate_set(self, target_id: int, num_candidates: int = 4) -> List[Image]:
        """Get target image and distractors."""
        target = self.dataset[target_id]
        self.current_target = target
        
        # Get random distractors
        distractors = random.sample(
            [img for img in self.dataset if img.id != target_id],
            min(num_candidates - 1, len(self.dataset) - 1)
        )
        
        candidate_set = [target] + distractors
        random.shuffle(candidate_set)
        return candidate_set


class SpeakerAgent:
    """
    Speaker Agent: Describes images using natural language.
    
    Uses functional learning (RL rewards) and structural learning (templates)
    to generate descriptions.
    """
    
    # Natural language templates for structural learning
    DESCRIPTION_TEMPLATES = [
        "A {size} {color} {shape}",
        "There is a {color} {shape}, {size} in size",
        "The image shows a {size} {color} {shape}",
        "I see a {color} {shape} that is {size}",
        "A {size} {shape} colored {color}",
        "The {color} {shape} is {size}",
    ]
    
    # Extended templates for variety
    EXTENDED_TEMPLATES = [
        "A {size} {color} {shape} positioned at the {position}",
        "The {color} {shape} in the image is {size}, located {position}",
        "An image of a {size} {color} {shape} at {position}",
        "I can see a {color} {shape} ({size}) in the {position}",
        "The {size} {color} {shape} is in the {position} area",
    ]
    
    def __init__(self, learning_rate: float = 0.1):
        """Initialize speaker agent with learning capabilities."""
        self.learning_rate = learning_rate
        self.vocabulary = {}
        self.reward_history = []
        self.use_extended_templates = False
        
    def describe_image(self, image: Image, use_position: bool = False) -> str:
        """
        Generate description of image.
        
        Args:
            image: Image object to describe
            use_position: Whether to include position in description
            
        Returns:
            Natural language description
        """
        templates = self.EXTENDED_TEMPLATES if use_position else self.DESCRIPTION_TEMPLATES
        template = random.choice(templates)
        
        # Structural learning: use template for grammatically correct output
        description = template.format(
            color=image.color,
            shape=image.shape,
            size=image.size,
            position=image.position
        )
        
        return description
    
    def generate_multiple_descriptions(self, image: Image, num_options: int = 5) -> List[str]:
        """Generate multiple description candidates for reranking."""
        descriptions = []
        for _ in range(num_options):
            desc = self.describe_image(image, use_position=random.random() > 0.3)
            if desc not in descriptions:  # Avoid duplicates
                descriptions.append(desc)
        
        # Fill remaining with variations if needed
        while len(descriptions) < num_options:
            desc = self.describe_image(image, use_position=random.random() > 0.3)
            if desc not in descriptions:
                descriptions.append(desc)
        
        return descriptions[:num_options]
    
    def update_with_reward(self, reward: float, description: str):
        """
        Functional learning: Update agent based on communication success reward.
        
        Args:
            reward: Reward signal (1.0 for success, 0.0 for failure)
            description: The description that was rewarded
        """
        self.reward_history.append(reward)
        
        # Simple Q-learning style update
        if reward > 0.5:  # Positive reward
            # Increase likelihood of using this type of description
            self.use_extended_templates = True
        else:
            # Explore more
            self.use_extended_templates = False


class ListenerAgent:
    """
    Listener Agent: Selects correct image from candidates based on description.
    
    Uses semantic understanding to match descriptions to images.
    """
    
    def __init__(self):
        """Initialize listener agent."""
        self.accuracy_history = []
        self.understanding_scores = {}
        
    def compute_similarity(self, description: str, image: Image) -> float:
        """
        Compute semantic similarity between description and image.
        Simple rule-based approach for demonstration.
        
        Args:
            description: Natural language description
            image: Image to match against
            
        Returns:
            Similarity score (0-1)
        """
        score = 0.0
        max_score = 0.0
        
        # Check color match
        max_score += 1.0
        if image.color.lower() in description.lower():
            score += 1.0
        
        # Check shape match
        max_score += 1.0
        if image.shape.lower() in description.lower():
            score += 1.0
        
        # Check size match
        max_score += 1.0
        if image.size.lower() in description.lower():
            score += 1.0
        
        # Check position match
        max_score += 1.0
        if image.position.lower() in description.lower():
            score += 0.8  # Lower weight if position not mentioned
        
        # Normalize
        return score / max_score if max_score > 0 else 0.5
    
    def select_image(self, description: str, candidates: List[Image]) -> Tuple[Image, float]:
        """
        Select image that best matches description.
        
        Args:
            description: Description from speaker
            candidates: List of candidate images
            
        Returns:
            Selected image and confidence score
        """
        scores = [(img, self.compute_similarity(description, img)) for img in candidates]
        best_image, confidence = max(scores, key=lambda x: x[1])
        
        return best_image, confidence
    
    def evaluate_match(self, selected: Image, target: Image) -> float:
        """
        Evaluate if selected image matches target.
        
        Returns:
            1.0 if correct, 0.0 if incorrect
        """
        # Check if all attributes match
        is_correct = (
            selected.color == target.color and
            selected.shape == target.shape and
            selected.size == target.size
        )
        
        return 1.0 if is_correct else 0.0


class RewardLearningRanker:
    """
    Reward-Learned Reranking System.
    
    Combines multiple descriptions using a reward signal to select
    the best one for the task.
    
    Based on key contribution from the paper.
    """
    
    def __init__(self):
        """Initialize reranking system."""
        self.description_rewards = {}
        self.reranking_history = []
        
    def rank_descriptions(self, 
                        descriptions: List[str], 
                        candidates: List[Image],
                        target: Image,
                        listener: ListenerAgent) -> str:
        """
        Rank descriptions based on communication success.
        
        Args:
            descriptions: List of candidate descriptions
            candidates: Images available to listener
            target: Target image
            listener: Listener agent for evaluation
            
        Returns:
            Best description for this communication task
        """
        best_description = None
        best_score = -1
        
        for description in descriptions:
            # Test each description
            selected, confidence = listener.select_image(description, candidates)
            task_reward = listener.evaluate_match(selected, target)
            
            # Combine task success and confidence
            combined_score = task_reward * confidence
            
            # Update tracking
            if description not in self.description_rewards:
                self.description_rewards[description] = []
            self.description_rewards[description].append(task_reward)
            
            if combined_score > best_score:
                best_score = combined_score
                best_description = description
        
        self.reranking_history.append({
            'best_description': best_description,
            'score': best_score
        })
        
        return best_description if best_description else descriptions[0]
    
    def get_ranking_statistics(self) -> Dict:
        """Get statistics about reranking performance."""
        if not self.reranking_history:
            return {}
        
        scores = [h['score'] for h in self.reranking_history]
        avg_score = sum(scores) / len(scores) if scores else 0
        return {
            'avg_score': avg_score,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'total_rounds': len(self.reranking_history)
        }
