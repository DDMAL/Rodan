/**
 * General utilities.
 */
export default class Utilities
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS - Static
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Copy text to clipboard. Returns true if "document.execCommand('copy')" is supported.
     *
     * @param {string} text string to copy to clipboard
     * @return {boolean} returns true if no error on "document.execCommand('copy')"
     */
    static copyTextToClipboard(text)
    {
        var returnValue = true;
        var target = document.createElement("textarea");
        var targetId = "_hiddenCopyText_";
        target.style.position = "absolute";
        target.style.left = "-9999px";
        target.style.top = "0";
        target.id = targetId;
        document.body.appendChild(target);
        target.textContent = text;
        var currentFocus = document.activeElement;
        target.focus();
        target.setSelectionRange(0, target.value.length);
        var succeed = false;
        try 
        {
            succeed = document.execCommand("copy");
        } 
        catch(e)
        {
            returnValue = false;
        }
        if (currentFocus && typeof currentFocus.focus === "function")
        {
            currentFocus.focus();
        }
        document.body.removeChild(target);
        return returnValue;
    }
}