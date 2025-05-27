/**
 * Utility functions for manipulating Glyph class names.
 *
 * @module ClassNameUtils
 */
export default {
    /**
     * Given a class name, remove illegal characters.
     *
     * @param {string} input - The name to sanitize.
     * @returns {string}
     */
    sanitizeClassName: function (input)
    {
        // Enforce string
        input = String(input);
        // Lowercase
        input = input.toLowerCase();
        // Remove everything other than letters and periods
        input = input.replace(/[^a-z\.\_0-9]/g, "");
        // Remove periods from beginning and end
        input = this.trimCharacter(input, '.');
        // Remove double periods
        input = input.replace(/\.{2,}/g, ".");
        return input;
    },

    /**
     * Given a string, strip away leading or trailing instances of char.
     *
     * @param {string} string - String to strip from.
     * @param {char} char - Character to strip away.
     * @returns {string} The stripped string.
     */
    trimCharacter: function (string, char)
    {
        if (!string || string.length < 1)
        {
            return "";
        }

        var leading = 0,
            trailing = 0;

        if (string.charAt(0) === char)
        {
            leading = 1;
        }
        if (string.charAt(string.length - 1) === char)
        {
            trailing = 1;
        }

        if (leading === 0 && trailing === 0)
        {
            return string;
        }
        else
        {
            string = string.substr(leading, string.length - trailing);
            return this.trimCharacter(string, char);
        }
    }
}
