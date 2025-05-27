let _os = null;
let _keyControls = {
    'Windows': {
        'range': 'shiftKey',
        'multiple': 'ctrlKey'
    },
    'MacOS': {
        'range': 'shiftKey',
        'multiple': 'metaKey'
    },
    'Linux': {
        'range': 'shiftKey',
        'multiple': 'ctrlKey'
    },
    'UNIX': {
        'range': 'shiftKey',
        'multiple': 'ctrlKey'
    },
    'Unknown OS': {
        'range': 'shiftKey',
        'multiple': 'ctrlKey'
    }
};

/**
 * Global environment constants.
 */
export default class Environment
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS - Static
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Returns string denoting detected operating system.
     *
     * @return {string} 'Windows', 'MacOS', 'UNIX', 'Linux', or 'Unknown OS'
     */
    static getOS()
    {
        if (_os === null)
        {
            _os = 'Unknown OS';
            if (navigator.appVersion.indexOf('Win') !== -1)
            {
                _os='Windows';
            }
            if (navigator.appVersion.indexOf('Mac') !== -1)
            {
                _os = 'MacOS';
            }
            if (navigator.appVersion.indexOf('X11') !== -1)
            {
                _os = 'UNIX';
            }
            if (navigator.appVersion.indexOf('Linux') !== -1)
            {
                _os = 'Linux';
            }
        }
        return _os;
    }

    /**
     * Get multiple selection key.
     *
     * @return {string} returns 'contol' or 'command', depending on OS
     */
    static getMultipleSelectionKey()
    {
        return _keyControls[Environment.getOS()].multiple;
    }

    /**
     * Get range selection key.
     *
     * @return {string} returns range selection key (e.g. 'shift'), depending on OS
     */
    static getRangeSelectionKey()
    {
        return _keyControls[Environment.getOS()].range;
    }
}