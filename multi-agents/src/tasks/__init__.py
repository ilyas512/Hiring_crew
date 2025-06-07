"""
Multi-Agent Recruitment System - Tasks Module
"""

from .job_offer_task import job_offer_task
from .cv_task import cv_task
from .rank_task import rank_task
from .quiz_generator_task import quiz_task
from .form_distribution_task import form_distribution_task

__all__ = [
    'job_offer_task',
    'cv_task',
    'rank_task', 
    'quiz_task',
    'form_distribution_task'
]