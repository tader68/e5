#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import (
    User, VocabularyWord, UserVocabulary, GrammarTopic, GrammarProgress,
    WritingTask, ReadingText, ReadingQuestion, ReadingProgress,
    Achievement, League
)
from datetime import datetime
import json
import os

def init_db():
    """Initialize the database with required data"""
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Initialize leagues
        init_leagues()
        
        # Initialize achievements
        init_achievements()
        
        print("Database initialized successfully!")

def init_leagues():
    """Initialize league data"""
    # Check if leagues already exist
    if League.query.first():
        print("Leagues already initialized!")
        return
        
    leagues = [
        {'name': 'Bronze', 'rank': 1},
        {'name': 'Silver', 'rank': 2},
        {'name': 'Gold', 'rank': 3},
        {'name': 'Sapphire', 'rank': 4},
        {'name': 'Ruby', 'rank': 5},
        {'name': 'Diamond', 'rank': 6}
    ]
    
    for league_data in leagues:
        league = League(**league_data)
        db.session.add(league)
    
    db.session.commit()
    print(f"Added {len(leagues)} leagues")

def init_achievements():
    """Initialize achievement data"""
    # Check if achievements already exist
    if Achievement.query.first():
        print("Achievements already initialized!")
        return
        
    achievements = [
        # Streak achievements
        {
            'name_key': 'streak_3',
            'description_key': 'streak_3_desc',
            'icon': 'fire',
            'category': 'streak',
            'xp_reward': 50,
            'gem_reward': 3,
            'condition_type': 'streak',
            'condition_value': 3
        },
        {
            'name_key': 'streak_7',
            'description_key': 'streak_7_desc',
            'icon': 'fire-alt',
            'category': 'streak',
            'xp_reward': 100,
            'gem_reward': 7,
            'condition_type': 'streak',
            'condition_value': 7
        },
        {
            'name_key': 'streak_14',
            'description_key': 'streak_14_desc',
            'icon': 'fire-alt',
            'category': 'streak',
            'xp_reward': 200,
            'gem_reward': 14,
            'condition_type': 'streak',
            'condition_value': 14
        },
        {
            'name_key': 'streak_30',
            'description_key': 'streak_30_desc',
            'icon': 'fire-alt',
            'category': 'streak',
            'xp_reward': 500,
            'gem_reward': 30,
            'condition_type': 'streak',
            'condition_value': 30
        },
        {
            'name_key': 'streak_100',
            'description_key': 'streak_100_desc',
            'icon': 'crown',
            'category': 'streak',
            'xp_reward': 1000,
            'gem_reward': 100,
            'condition_type': 'streak',
            'condition_value': 100
        },
        {
            'name_key': 'streak_365',
            'description_key': 'streak_365_desc',
            'icon': 'trophy',
            'category': 'streak',
            'xp_reward': 3000,
            'gem_reward': 365,
            'condition_type': 'streak',
            'condition_value': 365
        },
        
        # Vocabulary achievements
        {
            'name_key': 'first_word',
            'description_key': 'first_word_desc',
            'icon': 'star',
            'category': 'vocabulary',
            'xp_reward': 20,
            'gem_reward': 1,
            'condition_type': 'vocab_count',
            'condition_value': 1
        },
        {
            'name_key': 'collection_10',
            'description_key': 'collection_10_desc',
            'icon': 'book',
            'category': 'vocabulary',
            'xp_reward': 50,
            'gem_reward': 5,
            'condition_type': 'vocab_count',
            'condition_value': 10
        },
        {
            'name_key': 'collection_50',
            'description_key': 'collection_50_desc',
            'icon': 'books',
            'category': 'vocabulary',
            'xp_reward': 150,
            'gem_reward': 15,
            'condition_type': 'vocab_count',
            'condition_value': 50
        },
        {
            'name_key': 'collection_100',
            'description_key': 'collection_100_desc',
            'icon': 'book-reader',
            'category': 'vocabulary',
            'xp_reward': 300,
            'gem_reward': 30,
            'condition_type': 'vocab_count',
            'condition_value': 100
        },
        {
            'name_key': 'collection_500',
            'description_key': 'collection_500_desc',
            'icon': 'graduation-cap',
            'category': 'vocabulary',
            'xp_reward': 1000,
            'gem_reward': 100,
            'condition_type': 'vocab_count',
            'condition_value': 500
        },
        {
            'name_key': 'first_mastered',
            'description_key': 'first_mastered_desc',
            'icon': 'check-circle',
            'category': 'vocabulary',
            'xp_reward': 30,
            'gem_reward': 3,
            'condition_type': 'vocab_mastered',
            'condition_value': 1
        },
        {
            'name_key': 'mastered_10',
            'description_key': 'mastered_10_desc',
            'icon': 'check-double',
            'category': 'vocabulary',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'vocab_mastered',
            'condition_value': 10
        },
        {
            'name_key': 'mastered_50',
            'description_key': 'mastered_50_desc',
            'icon': 'certificate',
            'category': 'vocabulary',
            'xp_reward': 300,
            'gem_reward': 30,
            'condition_type': 'vocab_mastered',
            'condition_value': 50
        },
        {
            'name_key': 'mastered_100',
            'description_key': 'mastered_100_desc',
            'icon': 'award',
            'category': 'vocabulary',
            'xp_reward': 500,
            'gem_reward': 50,
            'condition_type': 'vocab_mastered',
            'condition_value': 100
        },
        
        # Grammar achievements
        {
            'name_key': 'grammar_first',
            'description_key': 'grammar_first_desc',
            'icon': 'pencil-alt',
            'category': 'grammar',
            'xp_reward': 30,
            'gem_reward': 3,
            'condition_type': 'grammar_completed',
            'condition_value': 1
        },
        {
            'name_key': 'grammar_5',
            'description_key': 'grammar_5_desc',
            'icon': 'pencil',
            'category': 'grammar',
            'xp_reward': 75,
            'gem_reward': 7,
            'condition_type': 'grammar_completed',
            'condition_value': 5
        },
        {
            'name_key': 'grammar_15',
            'description_key': 'grammar_15_desc',
            'icon': 'edit',
            'category': 'grammar',
            'xp_reward': 200,
            'gem_reward': 20,
            'condition_type': 'grammar_completed',
            'condition_value': 15
        },
        {
            'name_key': 'grammar_master',
            'description_key': 'grammar_master_desc',
            'icon': 'award',
            'category': 'grammar',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'grammar_mastered',
            'condition_value': 5
        },
        {
            'name_key': 'grammar_expert',
            'description_key': 'grammar_expert_desc',
            'icon': 'graduation-cap',
            'category': 'grammar',
            'xp_reward': 300,
            'gem_reward': 30,
            'condition_type': 'grammar_mastered',
            'condition_value': 15
        },
        
        # Writing achievements
        {
            'name_key': 'first_essay',
            'description_key': 'first_essay_desc',
            'icon': 'pen-fancy',
            'category': 'writing',
            'xp_reward': 50,
            'gem_reward': 5,
            'condition_type': 'writing_count',
            'condition_value': 1
        },
        {
            'name_key': 'writing_5',
            'description_key': 'writing_5_desc',
            'icon': 'pen',
            'category': 'writing',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'writing_count',
            'condition_value': 5
        },
        {
            'name_key': 'writing_expert',
            'description_key': 'writing_expert_desc',
            'icon': 'feather-alt',
            'category': 'writing',
            'xp_reward': 150,
            'gem_reward': 15,
            'condition_type': 'writing_count',
            'condition_value': 10
        },
        {
            'name_key': 'writing_master',
            'description_key': 'writing_master_desc',
            'icon': 'feather',
            'category': 'writing',
            'xp_reward': 300,
            'gem_reward': 30,
            'condition_type': 'writing_count',
            'condition_value': 25
        },
        
        # Reading achievements
        {
            'name_key': 'first_reading',
            'description_key': 'first_reading_desc',
            'icon': 'glasses',
            'category': 'reading',
            'xp_reward': 50,
            'gem_reward': 5,
            'condition_type': 'reading_count',
            'condition_value': 1
        },
        {
            'name_key': 'reading_5',
            'description_key': 'reading_5_desc',
            'icon': 'book-open',
            'category': 'reading',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'reading_count',
            'condition_value': 5
        },
        {
            'name_key': 'reading_expert',
            'description_key': 'reading_expert_desc',
            'icon': 'book',
            'category': 'reading',
            'xp_reward': 150,
            'gem_reward': 15,
            'condition_type': 'reading_count',
            'condition_value': 10
        },
        {
            'name_key': 'reading_master',
            'description_key': 'reading_master_desc',
            'icon': 'bookmark',
            'category': 'reading',
            'xp_reward': 300,
            'gem_reward': 30,
            'condition_type': 'reading_count',
            'condition_value': 25
        },
        
        # Level achievements
        {
            'name_key': 'level_5',
            'description_key': 'level_5_desc',
            'icon': 'signal',
            'category': 'level',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'user_level',
            'condition_value': 5
        },
        {
            'name_key': 'level_10',
            'description_key': 'level_10_desc',
            'icon': 'chart-line',
            'category': 'level',
            'xp_reward': 200,
            'gem_reward': 20,
            'condition_type': 'user_level',
            'condition_value': 10
        },
        {
            'name_key': 'level_25',
            'description_key': 'level_25_desc',
            'icon': 'medal',
            'category': 'level',
            'xp_reward': 500,
            'gem_reward': 50,
            'condition_type': 'user_level',
            'condition_value': 25
        },
        
        # League achievements
        {
            'name_key': 'join_league',
            'description_key': 'join_league_desc',
            'icon': 'users',
            'category': 'league',
            'xp_reward': 50,
            'gem_reward': 5,
            'condition_type': 'join_league',
            'condition_value': 1
        },
        {
            'name_key': 'top_ten',
            'description_key': 'top_ten_desc',
            'icon': 'trophy',
            'category': 'league',
            'xp_reward': 100,
            'gem_reward': 10,
            'condition_type': 'league_rank',
            'condition_value': 10
        },
        {
            'name_key': 'top_three',
            'description_key': 'top_three_desc',
            'icon': 'medal',
            'category': 'league',
            'xp_reward': 200,
            'gem_reward': 20,
            'condition_type': 'league_rank',
            'condition_value': 3
        },
        {
            'name_key': 'league_winner',
            'description_key': 'league_winner_desc',
            'icon': 'crown',
            'category': 'league',
            'xp_reward': 500,
            'gem_reward': 50,
            'condition_type': 'league_rank',
            'condition_value': 1
        }
    ]
    
    for achievement_data in achievements:
        achievement = Achievement(**achievement_data)
        db.session.add(achievement)
    
    db.session.commit()
    print(f"Added {len(achievements)} achievements")

if __name__ == '__main__':
    init_db()
