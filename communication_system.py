"""
Multi-Agent Communication System: Training and Evaluation.

Implements communication loops with different learning strategies as described
in the paper:
1. Functional Learning Only (RL)
2. Structural Learning Only (Language Models)
3. Combined Learning (Hybrid approach)
"""

import io
import random
from typing import List, Dict, Tuple
from contextlib import redirect_stdout
from agents import (
    SpeakerAgent, ListenerAgent, RewardLearningRanker, ImageEnvironment
)


class CommunicationSystem:
    """
    Orchestrates communication between speaker and listener agents.
    
    Implements different learning approaches for natural language
    multi-agent communication.
    """
    
    def __init__(self, env: ImageEnvironment, seed: int = 42):
        """Initialize communication system."""
        import random
        random.seed(seed)
        self.env = env
        self.episode_history = []
        
    def _run_communication_round(self,
                                speaker: SpeakerAgent,
                                listener: ListenerAgent,
                                target_id: int,
                                use_reranking: bool = False,
                                ranker: RewardLearningRanker = None) -> Dict:
        """
        Run one round of communication.
        
        Args:
            speaker: Speaker agent
            listener: Listener agent
            target_id: ID of target image
            use_reranking: Whether to use reward-learned reranking
            ranker: Reranking system (required if use_reranking=True)
            
        Returns:
            Dictionary with communication results
        """
        # Get candidate set
        candidates = self.env.get_candidate_set(target_id)
        target = self.env.current_target
        
        # Speaker describes the image
        if use_reranking and ranker:
            # Functional + Structural Learning: Generate and rerank
            descriptions = speaker.generate_multiple_descriptions(target)
            description = ranker.rank_descriptions(descriptions, candidates, target, listener)
        else:
            # Structural Learning Only: Simple description
            description = speaker.describe_image(target)
        
        # Listener selects image
        selected, confidence = listener.select_image(description, candidates)
        
        # Evaluate communication success
        success = listener.evaluate_match(selected, target)
        
        # Update speaker with reward (Functional Learning)
        speaker.update_with_reward(success, description)
        
        return {
            'target': target,
            'description': description,
            'selected': selected,
            'success': success,
            'confidence': confidence,
            'correct': selected.id == target.id
        }
    
    def functional_learning_only(self, 
                                num_episodes: int = 50,
                                episode_length: int = 10) -> Dict:
        """
        Experiment 1: Functional Learning Only (Multi-Agent RL).
        
        Agents learn through task-based interaction and rewards.
        Communication may develop artificial/non-human language.
        
        Returns:
            Performance metrics
        """
        print("=" * 70)
        print("FUNCTIONAL LEARNING ONLY (Multi-Agent RL)")
        print("=" * 70)
        
        speaker = SpeakerAgent()
        listener = ListenerAgent()
        
        total_success = 0
        episode_results = []
        
        for episode in range(num_episodes):
            episode_success = 0
            
            for step in range(episode_length):
                target_id = random.randint(0, len(self.env.dataset) - 1)
                result = self._run_communication_round(
                    speaker, listener, target_id, use_reranking=False
                )
                episode_success += result['success']
            
            accuracy = episode_success / episode_length
            episode_results.append(accuracy)
            total_success += episode_success
            
            if (episode + 1) % 10 == 0:
                print(f"Episode {episode + 1:3d}: Accuracy = {accuracy:.2%}")
        
        final_accuracy = total_success / (num_episodes * episode_length)
        
        print(f"\nFinal Accuracy: {final_accuracy:.2%}")
        print(f"Speaker reward history (last 50): {speaker.reward_history[-50:]}")
        print()
        
        return {
            'name': 'Functional Learning Only',
            'final_accuracy': final_accuracy,
            'episode_accuracies': episode_results,
            'speaker_rewards': speaker.reward_history
        }
    
    def structural_learning_only(self, 
                                num_episodes: int = 50,
                                episode_length: int = 10) -> Dict:
        """
        Experiment 2: Structural Learning Only (Language Model Templates).
        
        Agents use pre-defined language templates for grammatically correct
        but task-unaware communication.
        
        Returns:
            Performance metrics
        """
        print("=" * 70)
        print("STRUCTURAL LEARNING ONLY (Language Model Templates)")
        print("=" * 70)
        
        speaker = SpeakerAgent()
        listener = ListenerAgent()
        
        total_success = 0
        episode_results = []
        
        for episode in range(num_episodes):
            episode_success = 0
            
            for step in range(episode_length):
                target_id = random.randint(0, len(self.env.dataset) - 1)
                result = self._run_communication_round(
                    speaker, listener, target_id, use_reranking=False
                )
                episode_success += result['success']
            
            accuracy = episode_success / episode_length
            episode_results.append(accuracy)
            total_success += episode_success
            
            if (episode + 1) % 10 == 0:
                print(f"Episode {episode + 1:3d}: Accuracy = {accuracy:.2%}")
        
        final_accuracy = total_success / (num_episodes * episode_length)
        
        print(f"\nFinal Accuracy: {final_accuracy:.2%}")
        print("(Note: Template-based approach may lack task optimization)")
        print()
        
        return {
            'name': 'Structural Learning Only',
            'final_accuracy': final_accuracy,
            'episode_accuracies': episode_results,
            'speaker_rewards': speaker.reward_history
        }
    
    def combined_learning_reranking(self, 
                                   num_episodes: int = 50,
                                   episode_length: int = 10) -> Dict:
        """
        Experiment 3: Combined Learning with Reward-Learned Reranking.
        
        Integrates functional learning (RL rewards) and structural learning
        (language templates). The ranker selects descriptions that maintain
        natural language quality while optimizing for task success.
        
        Key innovation from the paper: Combines best of both approaches.
        
        Returns:
            Performance metrics
        """
        print("=" * 70)
        print("COMBINED LEARNING (Reward-Learned Reranking)")
        print("=" * 70)
        
        speaker = SpeakerAgent()
        listener = ListenerAgent()
        ranker = RewardLearningRanker()
        
        total_success = 0
        episode_results = []
        
        for episode in range(num_episodes):
            episode_success = 0
            
            for step in range(episode_length):
                target_id = random.randint(0, len(self.env.dataset) - 1)
                result = self._run_communication_round(
                    speaker, listener, target_id, 
                    use_reranking=True, ranker=ranker
                )
                episode_success += result['success']
            
            accuracy = episode_success / episode_length
            episode_results.append(accuracy)
            total_success += episode_success
            
            if (episode + 1) % 10 == 0:
                print(f"Episode {episode + 1:3d}: Accuracy = {accuracy:.2%}")
        
        final_accuracy = total_success / (num_episodes * episode_length)
        
        print(f"\nFinal Accuracy: {final_accuracy:.2%}")
        ranking_stats = ranker.get_ranking_statistics()
        if ranking_stats:
            print(f"Reranking Stats: {ranking_stats}")
        print("(Combined approach balances naturalness and task performance)")
        print()
        
        return {
            'name': 'Combined Learning (Reward-Learned Reranking)',
            'final_accuracy': final_accuracy,
            'episode_accuracies': episode_results,
            'speaker_rewards': speaker.reward_history,
            'ranker_stats': ranking_stats
        }
    
    def run_all_experiments(self, num_episodes: int = 50, episode_length: int = 10) -> List[Dict]:
        """
        Run all three learning approaches for comparison.
        
        Implements the paper's experimental framework comparing:
        1. Pure RL (functional learning)
        2. Pure language model (structural learning)
        3. Hybrid (combined learning)
        
        Returns:
            List of results from each approach
        """
        print("\n")
        print("#" * 70)
        print("# MULTI-AGENT COMMUNICATION SYSTEM EXPERIMENTS")
        print("# Based on: 'Multi-agent Communication meets Natural Language'")
        print("#" * 70)
        print("\n")
        
        results = []
        
        # Experiment 1
        result1 = self.functional_learning_only(num_episodes, episode_length)
        results.append(result1)
        
        # Reset for clean slate
        self.episode_history = []
        
        # Experiment 2
        result2 = self.structural_learning_only(num_episodes, episode_length)
        results.append(result2)
        
        # Reset for clean slate
        self.episode_history = []
        
        # Experiment 3
        result3 = self.combined_learning_reranking(num_episodes, episode_length)
        results.append(result3)
        
        return results

    def run_all_experiments_quiet(self,
                                  num_episodes: int = 30,
                                  episode_length: int = 10) -> Dict:
        """
        Run experiments without verbose console logs.

        Returns a compact summary suitable for terminal JSON output or web UIs.
        """
        # Capture existing print-heavy methods without modifying their behavior.
        with redirect_stdout(io.StringIO()):
            results = self.run_all_experiments(num_episodes, episode_length)

        best = max(results, key=lambda x: x['final_accuracy']) if results else None

        summaries = []
        for result in results:
            episode_accuracies = result.get('episode_accuracies', [])
            early_avg = (
                sum(episode_accuracies[:10]) / min(10, len(episode_accuracies))
                if episode_accuracies else 0.0
            )
            late_avg = (
                sum(episode_accuracies[-10:]) / min(10, len(episode_accuracies))
                if episode_accuracies else 0.0
            )
            summaries.append({
                'name': result.get('name', 'Unknown'),
                'final_accuracy': result.get('final_accuracy', 0.0),
                'early_avg': early_avg,
                'late_avg': late_avg,
                'improvement': late_avg - early_avg,
                'episode_accuracies': episode_accuracies,
            })

        return {
            'config': {
                'num_episodes': num_episodes,
                'episode_length': episode_length,
                'total_rounds_per_approach': num_episodes * episode_length,
            },
            'results': summaries,
            'best_approach': {
                'name': best['name'],
                'final_accuracy': best['final_accuracy'],
            } if best else None,
        }
    
    def print_comparison(self, results: List[Dict]):
        """Print comparison of all approaches."""
        print("\n")
        print("=" * 70)
        print("EXPERIMENT COMPARISON")
        print("=" * 70)
        
        print(f"\n{'Approach':<40} {'Final Accuracy':>20}")
        print("-" * 70)
        
        for result in results:
            accuracy_str = f"{result['final_accuracy']:.2%}"
            print(f"{result['name']:<40} {accuracy_str:>20}")
        
        # Find best
        best = max(results, key=lambda x: x['final_accuracy'])
        print("\n" + "=" * 70)
        print(f"BEST APPROACH: {best['name']}")
        print(f"Final Accuracy: {best['final_accuracy']:.2%}")
        print("=" * 70)
        print()


def demonstrate_communication():
    """Demonstrate a single communication session."""
    print("\n")
    print("=" * 70)
    print("DEMONSTRATION: Image Description Communication")
    print("=" * 70)
    print()
    
    env = ImageEnvironment(dataset_size=20)
    speaker = SpeakerAgent()
    listener = ListenerAgent()
    ranker = RewardLearningRanker()
    
    # Run a few examples
    for example in range(3):
        print(f"\n--- Example {example + 1} ---")
        
        target_id = random.randint(0, len(env.dataset) - 1)
        candidates = env.get_candidate_set(target_id)
        target = env.current_target
        
        print(f"Target: {target}")
        print(f"Candidates: {', '.join([f'Img{c.id}' for c in candidates])}")
        
        # Generate descriptions
        descriptions = speaker.generate_multiple_descriptions(target)
        print(f"\nGenerated descriptions:")
        for i, desc in enumerate(descriptions, 1):
            print(f"  {i}. {desc}")
        
        # Rerank
        best_desc = ranker.rank_descriptions(descriptions, candidates, target, listener)
        print(f"\nBest description (via reranking): {best_desc}")
        
        # Listener selects
        selected, confidence = listener.select_image(best_desc, candidates)
        success = listener.evaluate_match(selected, target)
        
        print(f"Selected: {selected} (confidence: {confidence:.2f})")
        print(f"Result: {'✓ SUCCESS' if success > 0.5 else '✗ FAILED'}")
    
    print("\n")


if __name__ == "__main__":
    # Demonstration
    demonstrate_communication()
    
    # Main experiments
    env = ImageEnvironment(dataset_size=50)
    system = CommunicationSystem(env)
    
    results = system.run_all_experiments(
        num_episodes=30,
        episode_length=10
    )
    
    system.print_comparison(results)
