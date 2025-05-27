/**
 * This object contains all of the strings to be used in HTML templates.
 *
 * @todo In the future, we could really easily localize the application by restructuring this object as a string factory that produces strings for the chosen language.
 *
 * @module Strings
 */

//jscs:disable maximumLineLength
export default {
    siteTitle: "Interactive Classifier",
    submissionWarning: "Your manual corrections will be sent back to Rodan for another round of Gamera classification. Once the classification is complete, you can make more manual corrections.",
    groupWarning: "Your manual corrections will be sent back to Rodan for a round of Gamera grouping and re-classification. Once the classification is complete, you can make more manual corrections.",
    finalizeText: "Your manual corrections will be sent back to Rodan for a final round of Gamera classification. The results will be saved, and the job will complete.",
    finalizeWarning: "You will not be able to do any more manual corrections!",
    openText: "Choose a file... did it work?",
    openWarning: "Are you sure you wish to do this?",
    loadingGlyphs: "Loading page glyphs from the server.  This may take some time...",
    submittingGlyphs: "Reclassifications of glyphs. This may take some time...",
    menuSubmitLabel: "Re-Classify",
    menuGroupLabel: "Group and Re-Classify",
    menuFinalizeLabel: "Finalize",
    menuOpenImage: "Open File",
    loadingPage: "Loading Page...",
    submittingCorrections: "Submitting Corrections",
    submitCorrections: "Submit Corrections...",
    submitAndGroup: "Submit and Group...",
    finalizeCorrections: "Finalize Corrections...",
    openTitle: "Open...",
    classes: "Classes",
    editGlyphLabel: "Edit",
    editGlyphDescription: "Click on a Glyph to edit it.",
    groupTitle: "Grouping",
    splitTitle: "Splitting",
    groupingGlyphs: "The Glyphs are being grouped...",
    splittingGlyph: "The Glyph is being split...",
    deleteWarning: "Are you sure you wish to delete multiple glyphs?",
    unclassifiedClass: "UNCLASSIFIED is a reserved keyword.",
    invalidClass: " is not a valid class name.",
    saveChanges: " Save",
    saveWarning: "Save the current state?",
    undoAll: " Revert",
    undoWarning: "Are you sure you wish to undo all changes? This will restore the original state of the job.",
    classifierGlyphs: " glyphs in classifier",
    pageGlyphs: " glyphs in page",
    selectedGlyphs: " selected glyphs",
    classNameError: "Invalid Class Name",
    deleteTitle: "Delete Multiple Glyphs",
    // Strings for GlyphEditview
    editGlyph: {
        update: "Update",
        connectedComponent: "Connected Components",
        classLabel: "Class",
        manualID: "Manual ID",
        confidence: "Confidence",
        position: "Position",
        dimensions: "Dimensions",
        glyphPreview: "Glyph Preview",
        split: "Split",
        delete: "Delete Glyph"
    },
    editClass: {
        update: "Update",
        className: "Name",
        deleteClass: "Delete Class",
        glyphs: "Glyphs"
    },
    glyphMultiEdit: {
        updateAllSelected: "Update All Selected",
        groupAllSelected: "Group All Selected",
        deleteAllSelected: "Delete All Selected"
    }
};
//jscs:enable maximumLineLength
