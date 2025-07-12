def switch_focus_mode(new_mode, dm=None):
    """Switch the focus mode for the user"""
    if not dm:
        return False
    try:
        # Load current settings
        settings = dm.load_data('user_settings')
        settings['focus_mode'] = new_mode
        dm.save_data('user_settings', settings)
        logger.info(f"Focus mode switched to {new_mode}")
        return True
    except Exception as e:
        logger.error(f"Error switching focus mode: {e}")
        return False
