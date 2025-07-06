"""
Focus Modes for Smart Påminner Pro
Ulike moduser for forskjellige brukerbehov
"""

from datetime import datetime, timedelta
import json

class FocusMode:
    """Base class for focus modes"""
    
    def __init__(self, name, description, settings):
        self.name = name
        self.description = description
        self.settings = settings
    
    def apply_to_reminders(self, reminders):
        """Apply focus mode settings to reminders"""
        return reminders
    
    def get_notification_settings(self):
        """Get notification preferences for this mode"""
        return self.settings.get('notifications', {})

class SilentMode(FocusMode):
    """Stillemodus - Minimale forstyrrelser"""
    
    def __init__(self):
        super().__init__(
            name="Stillemodus",
            description="Reduserte notifikasjoner, kun høy prioritet",
            settings={
                'notifications': {
                    'email_enabled': False,
                    'sound_enabled': False,
                    'priority_filter': ['Høy'],
                    'quiet_hours': {'start': '22:00', 'end': '08:00'}
                },
                'display': {
                    'simplified_view': True,
                    'reduced_colors': True,
                    'minimal_animations': True
                }
            }
        )
    
    def apply_to_reminders(self, reminders):
        """Filter til kun høy prioritet påminnelser"""
        return [r for r in reminders if r.get('priority') == 'Høy']

class ADHDMode(FocusMode):
    """ADHD-modus - Økt fokus og struktur"""
    
    def __init__(self):
        super().__init__(
            name="ADHD-modus",
            description="Ekstra påminnelser, farger og struktur",
            settings={
                'notifications': {
                    'email_enabled': True,
                    'sound_enabled': True,
                    'extra_reminders': True,
                    'reminder_intervals': [60, 30, 15, 5],  # minutter før
                    'color_coding': True
                },
                'display': {
                    'enhanced_colors': True,
                    'progress_bars': True,
                    'time_blocking': True,
                    'urgency_indicators': True
                }
            }
        )
    
    def apply_to_reminders(self, reminders):
        """Legg til ekstra visuell informasjon"""
        now = datetime.now()
        
        for reminder in reminders:
            try:
                reminder_time = datetime.fromisoformat(reminder['datetime'].replace(' ', 'T'))
                time_diff = reminder_time - now
                
                # Legg til urgency level
                if time_diff.total_seconds() < 3600:  # < 1 time
                    reminder['urgency'] = 'critical'
                elif time_diff.total_seconds() < 86400:  # < 1 dag
                    reminder['urgency'] = 'high'
                elif time_diff.total_seconds() < 604800:  # < 1 uke
                    reminder['urgency'] = 'medium'
                else:
                    reminder['urgency'] = 'low'
                
                # Legg til tidsestimering
                reminder['time_until'] = str(time_diff).split('.')[0]
                
            except Exception:
                reminder['urgency'] = 'low'
        
        # Sorter etter urgency
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        reminders.sort(key=lambda x: urgency_order.get(x.get('urgency', 'low'), 3))
        
        return reminders

class ElderlyMode(FocusMode):
    """Modus for eldre - Stor tekst og enkle funksjoner"""
    
    def __init__(self):
        super().__init__(
            name="Modus for eldre",
            description="Større tekst, enklere grensesnitt",
            settings={
                'notifications': {
                    'email_enabled': True,
                    'sound_enabled': True,
                    'repeat_notifications': True,
                    'large_text': True
                },
                'display': {
                    'large_fonts': True,
                    'high_contrast': True,
                    'simplified_ui': True,
                    'fewer_options': True,
                    'larger_buttons': True
                }
            }
        )

class WorkMode(FocusMode):
    """Jobbmodus - Fokus på jobb-relaterte påminnelser"""
    
    def __init__(self):
        super().__init__(
            name="Jobbmodus",
            description="Fokus på jobb, skjul private påminnelser",
            settings={
                'notifications': {
                    'email_enabled': True,
                    'category_filter': ['Jobb'],
                    'work_hours_only': True,
                    'work_hours': {'start': '08:00', 'end': '17:00'}
                },
                'display': {
                    'professional_theme': True,
                    'hide_personal': True
                }
            }
        )
    
    def apply_to_reminders(self, reminders):
        """Vis kun jobb-relaterte påminnelser i arbeidstid"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # Sjekk om det er arbeidstid
        if '08:00' <= current_time <= '17:00' and now.weekday() < 5:
            return [r for r in reminders if r.get('category') == 'Jobb']
        
        return reminders

class StudyMode(FocusMode):
    """Studiemodus - Fokus på læring og deadlines"""
    
    def __init__(self):
        super().__init__(
            name="Studiemodus",
            description="Fokus på studier og deadlines",
            settings={
                'notifications': {
                    'email_enabled': True,
                    'deadline_alerts': True,
                    'study_breaks': True,
                    'pomodoro_timer': True
                },
                'display': {
                    'deadline_countdown': True,
                    'progress_tracking': True,
                    'study_statistics': True
                }
            }
        )

class DrivingSchoolMode(FocusMode):
    """Kjøreskolemodus - Eier og instruktører kan sende påminnelser til hverandre"""
    def __init__(self):
        super().__init__(
            name="Kjøreskolemodus",
            description="Eier og instruktører kan sende påminnelser til hverandre. Spesialtilpasset for kjøreskoler.",
            settings={
                'notifications': {
                    'email_enabled': True,
                    'sound_enabled': True,
                    'allow_instructor_to_owner': True,
                    'allow_owner_to_instructor': True
                },
                'display': {
                    'show_instructor_tools': True,
                    'show_owner_tools': True
                }
            }
        )
    def apply_to_reminders(self, reminders):
        # Ingen spesiell filtrering, men kan utvides
        return reminders

# Focus Mode Manager
class FocusModeManager:
    """Håndterer fokusmoduser for brukere"""
    
    AVAILABLE_MODES = {
        'normal': FocusMode("Normal", "Standard innstillinger", {}),
        'silent': SilentMode(),
        'adhd': ADHDMode(),
        'elderly': ElderlyMode(),
        'work': WorkMode(),
        'study': StudyMode(),
        'driving_school': DrivingSchoolMode()
    }
    
    def __init__(self):
        self.current_mode = None

    def set_mode(self, mode):
        valid_modes = ['stillemodus', 'ADHD-modus', 'modus for eldre', 'jobbmodus', 'studiemodus', 'kjøreskolemodus']
        if mode in valid_modes:
            self.current_mode = mode
        else:
            raise ValueError('Ugyldig modus valgt')

    def get_mode(self):
        return self.current_mode
    
    @classmethod
    def get_mode_by_name(cls, mode_name):
        """Hent en spesifikk fokumodus"""
        return cls.AVAILABLE_MODES.get(mode_name, cls.AVAILABLE_MODES['normal'])
    
    @classmethod
    def get_all_modes(cls):
        """Hent alle tilgjengelige moduser"""
        return cls.AVAILABLE_MODES
    
    @classmethod
    def apply_mode_to_reminders(cls, reminders, mode_name):
        """Apply focus mode to reminders"""
        mode = cls.get_mode_by_name(mode_name)
        return mode.apply_to_reminders(reminders)
    
    @classmethod
    def get_mode_settings(cls, mode_name):
        """Get settings for a specific mode"""
        mode = cls.get_mode_by_name(mode_name)
        return mode.settings
