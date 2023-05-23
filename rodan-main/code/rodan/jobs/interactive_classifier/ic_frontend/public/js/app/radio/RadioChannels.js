import Radio from "backbone.radio";

/**
 * The set of radio channels currently used by the application.
 *
 * @module RadioChannels
 */
export default {
    /**
     * Channel for opening and closing modals.
     */
    modal: Radio.channel("modal"),
    /**
     * Channel for events relating to editing glyphs.
     */
    edit: Radio.channel("edit"),
    /**
     * Channel for events that fire when you click on menu buttons.
     */
    menu: Radio.channel("menu")
}