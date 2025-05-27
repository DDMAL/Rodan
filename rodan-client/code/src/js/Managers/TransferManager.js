import Backbone from 'backbone';
import Radio from 'backbone.radio';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';

/**
 * File transfer manager. This manages all file (i.e. Resource) uploads and downloads.
 */
export default class TransferManager
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Constructor.
     */
    constructor()
    {
        this._initializeRadio();
        this._uploadsPending = new Backbone.Collection();
        this._uploadsFailed = new Backbone.Collection();
        this._uploadsCompleted = new Backbone.Collection();
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize Radio.
     */
    _initializeRadio()
    {
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__TRANSFERMANAGER_DOWNLOAD, options => this._handleRequestDownload(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__TRANSFERMANAGER_GET_UPLOAD_COUNT, () => this._handleRequestGetUploadCount());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__TRANSFERMANAGER_MONITOR_UPLOAD, options => this._handleRequestMonitorUpload(options));
    }

    /**
     * Handle download request.
     */
    _handleRequestDownload(options)
    {
        var request = new XMLHttpRequest();
        request.open('GET', options.url, true);
        request.responseType = 'blob';
        request.onreadystatechange = (event) => this._handleStateChange(event, options.filename, options.mimetype);
        request.onprogress = (event) => this._handleDownloadProgress(event);
        request.send();
    }

    /**
     * Return upload count.
     */
    _handleRequestGetUploadCount()
    {
        return {pending: this._uploadsPending.length, completed: this._uploadsCompleted.length, failed: this._uploadsFailed.length};
    }

    /**
     * Handle request monitor upload.
     */
    _handleRequestMonitorUpload(options)
    {
        var request = options.request;
        request.id = this._getRandomId();
        options.id = request.id;
        this._uploadsPending.add(options);
        request.done((response, code, jqXHR) => this._handleUploadSuccess(response, code, jqXHR));
        request.fail((jqXHR, code, error) => this._handleUploadFail(jqXHR, code, error));
    }

    /**
     * Handle upload success.
     */
    _handleUploadSuccess(response, code, jqXHR)
    {
        var upload = this._uploadsPending.remove(jqXHR.id);
        this._uploadsCompleted.add(upload);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__TRANSFERMANAGER_UPLOAD_SUCCEEDED, {request: upload.jqXHR, file: upload.file});
    }

    /**
     * Handle upload fail.
     */
    _handleUploadFail(jqXHR, code, error)
    {
        var upload = this._uploadsPending.remove(jqXHR.id);
        this._uploadsFailed.add(upload);
        Radio.channel('rodan').trigger(RODAN_EVENTS.EVENT__TRANSFERMANAGER_UPLOAD_FAILED, {request: upload.jqXHR, file: upload.file});
    }

    /**
     * Handle request state change.
     */
    _handleStateChange(request, filename, mimetype)
    {
        switch (request.currentTarget.readyState)
        {
            case 0: //UNSENT
            {
                break;
            }

            case 1: //OPENED
            {
                break;
            }

            case 2: //HEADERS_RECEIVED
            {
                break;
            }

            case 3: //LOADING
            {
                break;
            }

            case 4:
            {
                Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__DOWNLOAD_START, {data: request.currentTarget.response, filename: filename, mimetype: mimetype});
                break;
            }

            default:
            {
                break;
            }
        }
    }

    /**
     * Handle download progress.
     */
    _handleDownloadProgress(event)
    {
    }

    /**
     * Returns random 8-digit ID.
     */
    _getRandomId()
    {
        return Math.floor((1 + Math.random()) * 10000000);
    }
}