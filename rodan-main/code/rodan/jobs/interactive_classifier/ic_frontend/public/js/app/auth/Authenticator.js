import $ from "jquery";

/**
 * This class maintains a `runjob.working_user_expiry` Rodan token throughout its lifetime.
 *
 * For more information, see {@link https://github.com/DDMAL/Interactive-Classifier/wiki/Token-Authentication}.
 */
export default class Authenticator {

    /**
     * Grabs the authentication URL from the page URL and sets the timeout
     * to 5000 miliseconds.
     */
    constructor()
    {
        // This will be the URL that we hit to authenticate.
        this._authUrl = Authenticator.getAuthUrl();
        // Authenticate every few seconds
        this._time = 5000;
    }

    /**
     * Start authenticating on an interval.
     */
    startTimedAuthentication()
    {
        var that = this;
        this._timer = setInterval(function ()
        {
            that.authenticate();
        }, this._time);
    }

    /**
     * Authenticate with the server then save the working POST url for when
     * we will submit to the server later.
     */
    authenticate()
    {
        var that = this;
        $.ajax({
            url: that._authUrl,
            type: 'POST',
            headers: {
                Accept: "application/json; charset=utf-8",
                "Content-Type": "application/json; charset=utf-8",
                Authorization: "Token " + document.cookie.split('; ').find(cookie => cookie.startsWith('token=')).split('=')[1]
            },
            complete: function (response)
            {
                /**
                * Get the working user token, and update it in the url,
                */
                var responseData = JSON.parse(response.responseText);
                that._workingUrl = responseData.working_url;
                var objectUUID = [that._workingUrl.split("/").slice(4, 6).join("/")];
                var workingUrlUpdated = '/interactive/' + objectUUID[0] + '/';
                window.history.pushState({urlPath: workingUrlUpdated},"", workingUrlUpdated);
            }
        });
    }

    /**
     * Get the working POST url for the Interactive Job.  This is the URL that
     * we make a post request to when we want to complete the interactive
     * portion of the interactive job.
     *
     * @returns {string} - The "working" URL on the server for the job.
     */
    getWorkingUrl()
    {
        return this._workingUrl;
    }

    /**
     * Get the authentication url.
     *
     * @returns {string} - The authentication URL.
     */
    static getAuthUrl()
    {
        return window.location.href.split("/").slice(0, -2).join("/") + "/acquire/";
    }
}
