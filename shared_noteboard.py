"""
Shared Noteboard for Smart Påminner Pro
Delte tavler hvor brukere kan samarbeide
"""

import uuid
import json
from datetime import datetime
from pathlib import Path

class SharedNoteboard:
    """Delt tavle klasse"""
    
    def __init__(self, board_id, title, description, created_by, access_code=None):
        self.board_id = board_id
        self.title = title
        self.description = description
        self.created_by = created_by
        self.access_code = access_code or self._generate_access_code()
        self.created_at = datetime.now().isoformat()
        self.members = [created_by]
        self.notes = []
        self.settings = {
            'public': False,
            'allow_anonymous': False,
            'moderation': False
        }
    
    def _generate_access_code(self):
        """Generer tilgangskode for tavlen"""
        return str(uuid.uuid4())[:8].upper()
    
    def add_note(self, content, author, note_type='text', color='yellow'):
        """Legg til en ny notis på tavlen"""
        note = {
            'id': str(uuid.uuid4()),
            'content': content,
            'author': author,
            'type': note_type,  # text, checklist, image, link
            'color': color,
            'position': {'x': 0, 'y': 0},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': [],
            'completed': False if note_type == 'checklist' else None
        }
        self.notes.append(note)
        return note
    
    def update_note(self, note_id, content=None, position=None, color=None):
        """Oppdater en eksisterende notis"""
        for note in self.notes:
            if note['id'] == note_id:
                if content is not None:
                    note['content'] = content
                if position is not None:
                    note['position'] = position
                if color is not None:
                    note['color'] = color
                note['updated_at'] = datetime.now().isoformat()
                return note
        return None
    
    def delete_note(self, note_id, user_email):
        """Slett en notis (kun oppretteren eller admin)"""
        for i, note in enumerate(self.notes):
            if note['id'] == note_id:
                if note['author'] == user_email or user_email == self.created_by:
                    del self.notes[i]
                    return True
        return False
    
    def add_member(self, email):
        """Legg til medlem på tavlen"""
        if email not in self.members:
            self.members.append(email)
    
    def remove_member(self, email):
        """Fjern medlem fra tavlen"""
        if email in self.members and email != self.created_by:
            self.members.remove(email)

class NoteboardManager:
    """Håndterer alle delte tavler"""
    
    def __init__(self, data_manager):
        self.dm = data_manager
        self.boards_file = 'shared_noteboards'
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Sørg for at data-fil eksisterer"""
        try:
            self.dm.load_data(self.boards_file)
        except:
            self.dm.save_data(self.boards_file, {})
    
    def create_board(self, title, description, created_by):
        """Opprett ny delt tavle"""
        board_id = str(uuid.uuid4())
        board = SharedNoteboard(board_id, title, description, created_by)
        
        boards = self.dm.load_data(self.boards_file)
        boards[board_id] = {
            'board_id': board.board_id,
            'title': board.title,
            'description': board.description,
            'created_by': board.created_by,
            'access_code': board.access_code,
            'created_at': board.created_at,
            'members': board.members,
            'notes': board.notes,
            'settings': board.settings
        }
        self.dm.save_data(self.boards_file, boards)
        
        return board
    
    def get_board_by_id(self, board_id):
        """Hent tavle ved ID"""
        boards = self.dm.load_data(self.boards_file)
        if board_id in boards:
            board_data = boards[board_id]
            board = SharedNoteboard(
                board_data['board_id'],
                board_data['title'],
                board_data['description'],
                board_data['created_by'],
                board_data['access_code']
            )
            board.created_at = board_data['created_at']
            board.members = board_data['members']
            board.notes = board_data['notes']
            board.settings = board_data['settings']
            return board
        return None
    
    def get_board_by_access_code(self, access_code):
        """Hent tavle ved tilgangskode"""
        boards = self.dm.load_data(self.boards_file)
        for board_data in boards.values():
            if board_data['access_code'] == access_code:
                return self.get_board_by_id(board_data['board_id'])
        return None
    
    def get_user_boards(self, user_email):
        """Hent alle tavler brukeren har tilgang til"""
        boards = self.dm.load_data(self.boards_file)
        user_boards = []
        
        for board_data in boards.values():
            if user_email in board_data['members']:
                board = self.get_board_by_id(board_data['board_id'])
                user_boards.append(board)
        
        return user_boards
    
    def save_board(self, board):
        """Lagre tavle"""
        boards = self.dm.load_data(self.boards_file)
        boards[board.board_id] = {
            'board_id': board.board_id,
            'title': board.title,
            'description': board.description,
            'created_by': board.created_by,
            'access_code': board.access_code,
            'created_at': board.created_at,
            'members': board.members,
            'notes': board.notes,
            'settings': board.settings
        }
        self.dm.save_data(self.boards_file, boards)
    
    def delete_board(self, board_id, user_email):
        """Slett tavle (kun oppretteren)"""
        board = self.get_board_by_id(board_id)
        if board and board.created_by == user_email:
            boards = self.dm.load_data(self.boards_file)
            if board_id in boards:
                del boards[board_id]
                self.dm.save_data(self.boards_file, boards)
                return True
        return False
    
    def join_board(self, access_code, user_email):
        """Bli med på en tavle ved tilgangskode"""
        board = self.get_board_by_access_code(access_code)
        if board:
            board.add_member(user_email)
            self.save_board(board)
            return board
        return None
