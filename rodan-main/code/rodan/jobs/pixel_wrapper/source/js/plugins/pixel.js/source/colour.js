/*jshint esversion: 6 */
export class Colour
{
    constructor (red, green, blue, alpha)
    {
        this.red = red;
        this.green = green;
        this.blue = blue;
        this.alpha = alpha;
    }

    /**
     * Turns the red, green, blue and opacity values into an HTML colour
     * @returns {string}
     */
    toHTMLColour ()
    {
        return "rgba(" + this.red +  ", " + this.green + ", " + this.blue + ", " + this.alpha + ")";
    }

    /**
     * Returns the Colour object in a hexadecimal string format (#RRGGBB)
     * @returns {string}
     */
    toHexString ()
    {
        let hexString = "#";

        let red = this.red.toString(16),
            green = this.green.toString(16),
            blue = this.blue.toString(16);

        if (red.length === 1)
            hexString = hexString.concat("0");
        hexString = hexString.concat(red);

        if (green.length === 1)
            hexString = hexString.concat("0");
        hexString = hexString.concat(green);

        if (blue.length === 1)
            hexString = hexString.concat("0");
        hexString = hexString.concat(blue);

        return hexString;
    }

    /**
     * Compares 2 colours to each other based on a certain tolerance
     * @param colour
     * @param tolerance
     * @returns {boolean}
     */
    isSimilarTo (colour, tolerance)
    {
        if (!((colour.red >= this.red - tolerance) && (colour.red <= this.red + tolerance)))
            return false;

        if (!((colour.blue >= this.blue - tolerance) && (colour.blue <= this.blue + tolerance)))
            return false;

        if (!((colour.green >= this.green - tolerance) && (colour.green <= this.green + tolerance)))
            return false;

        return true;
    }
}