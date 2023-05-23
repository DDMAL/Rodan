/**
 * Construct a recursive tree from a list of class names.
 *
 * The class names are split on the '.' character.
 *
 * So, the list ["a.b.c", "a.b.d", "a.c.c"] would become become:
 *
 *  - a
 *      -b
 *          -c
 *          -d
 *      -c
 *          -c
 *
 * @param classNames
 * @param root
 */
export default function (classNames, root)
{
    // Split up the class names by periods
    var splitNames = classNames.map(
        function (className)
        {
            return className.split('.');
        }
    );

    // Iterate through the split names, recursively adding to the root
    for (var i = 0; i < splitNames.length; i++)
    {
        var codeArray = splitNames[i];
        var node = root;
        for (var j = 0; j < codeArray.length; j++)
        {
            node = node.getOrAppendChild(codeArray[j]);
        }
    }
}
