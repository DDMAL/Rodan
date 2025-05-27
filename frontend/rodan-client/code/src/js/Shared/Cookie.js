/**
 * ES6 Port of the Cappuccino CPCookie Class.
 */
export default class Cookie
{
    /**
     * Constructor.
     *
     * @param {string} name name of cookie
     */
    constructor(name)
    {
        this._cookieName = name;
        this._cookieValue = this._readCookieValue();
        this._expires = null;
    }

    /**
     * Saves provided info as cookie.
     *
     * @param {string} name name of cookie
     * @param {string} value value of cookie
     * @param {integer} days days until expiration of cookie
     */
    static saveCookie(name, value, days)
    {
        var date = new Date();
        date.setTime(date.getTime() + (days * 86400000));
        var expires = 'expires=' + date.toUTCString();
        document.cookie = name + '=' + value + '; ' + expires;
    }

    /**
     * Returns name.
     *
     * @return {string} name
     */
    get name()
    {
        return this._cookieName;
    }

    /**
     * Returns value.
     *
     * @return {string} value
     */
    get value()
    {
        return this._cookieValue;
    }

    /**
     * Returns expiration date.
     *
     * @return {Date} expiration date
     */
    get expires()
    {
        return this._expires;
    }

    /**
     * Returns value of cookie.
     *
     * @return {string} value of cookie
     */
    _readCookieValue()
    {
        var name = this._cookieName + '=',
            ca = document.cookie.split(';');

        for (var i = 0, len = ca.length; i < len; i++)
        {
            var c = ca[i];
            while (c.charAt(0) === ' ')
            {
                c = c.substring(1, c.length);
            }

            if (c.indexOf(name) === 0)
            {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }
}