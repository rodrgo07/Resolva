# Estado global do Kill Switch em memória (com opção de reset imediato)
_KILL_SWITCH_ACTIVE: bool = False

def is_kill_switch_active() -> bool:
    global _KILL_SWITCH_ACTIVE
    return _KILL_SWITCH_ACTIVE

def activate_kill_switch() -> bool:
    global _KILL_SWITCH_ACTIVE
    _KILL_SWITCH_ACTIVE = True
    return True

def deactivate_kill_switch() -> bool:
    global _KILL_SWITCH_ACTIVE
    _KILL_SWITCH_ACTIVE = False
    return False
