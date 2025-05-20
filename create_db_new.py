#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import User, VocabularyWord, UserVocabulary, GrammarTopic, GrammarProgress, WritingTask, ReadingText, ReadingQuestion, ReadingProgress

app = create_app()

with app.app_context():
    # Create all tables in the database
    db.create_all()
    print("Database created successfully!")
    
    # Create admin account
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@lingoboost.com',
            level='C2'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
    else:
        print("Admin account already exists!") 