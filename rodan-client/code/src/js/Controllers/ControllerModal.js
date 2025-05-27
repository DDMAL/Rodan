import $ from 'jquery';
import _ from 'underscore';
import BaseController from './BaseController';
import RODAN_EVENTS from 'js/Shared/RODAN_EVENTS';
import Marionette from 'backbone.marionette';
import Radio from 'backbone.radio';

/**
 * Controls modals.
 */
export default class ControllerModal extends BaseController
{
///////////////////////////////////////////////////////////////////////////////////////
// PUBLIC METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initializes the instance.
     */
    initialize()
    {
        this._waiting = true;
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Initialize radio.
     */
    _initializeRadio()
    {
        // Requests.
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MODAL_ERROR, (options) => this._handleRequestModalError(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MODAL_HIDE, () => this._handleRequestModalHide());
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MODAL_SHOW, options => this._handleRequestModalShow(options));
        Radio.channel('rodan').reply(RODAN_EVENTS.REQUEST__MODAL_SHOW_IMPORTANT, options => this._handleRequestModalShowImportant(options));
    }

///////////////////////////////////////////////////////////////////////////////////////
// PRIVATE METHODS - Radio handlers
///////////////////////////////////////////////////////////////////////////////////////
    /**
     * Handle request modal hide.
     */
    _handleRequestModalHide()
    {
        var $modalElement = $('#modal-generic');
        $('.modal-footer').removeClass('modal-footer-error');
        $modalElement.hide();
        this._waiting = false;
    }

    /**
     * Handle request modal show.
     */
    _handleRequestModalShow(options)
    {
        console.log(options);
        var $modalEl = $('#modal-generic');
        console.log($modalEl);
        if ($modalEl.is(':visible'))
        {
            return;
        }

        if (typeof options.content == 'string')
        {
            this._layoutViewModal = new Marionette.View({ template: _.template($('#template-modal_simple').text()) });
            this._layoutViewModal.setElement('<div class="content-wrapper column-content"></div>');
            this._layoutViewModal.render();

            $modalEl.html(this._layoutViewModal.el);
            $('.modal-title').text(options.title);
            $('.modal-body').append(options.content);
            $('#modal-close').on('click', () => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE));      
        }
        else
        {
            this._layoutViewModal = new Marionette.View({ template: _.template($('#template-modal').text()) });
            this._layoutViewModal.setElement('<div class="content-wrapper column-content"></div>');
            this._layoutViewModal.addRegions({modal_body: '#region-modal_body'});
            this._layoutViewModal.render();
            this._layoutViewModal.showChildView('modal_body', options.content);

            $modalEl.html(this._layoutViewModal.el);
            $('.modal-title').text(options.title);
            $('#modal-close').on('click', () => Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_HIDE));         
        }

        switch (options.scroll) {
            case 'modal':
                $('.modal-body').addClass('modal-scroll');
                break;

            case 'table':
                $('.modal .table-responsive').css('height', '50vh');
                $('.modal .table-responsive>.table>tbody').addClass('tbody-scroll');
                break;
        }

        $modalEl.show();      
    }

    /**
     * Handles modal update footer. If a modal is currently visible, this will
     * update the footer. If not, it will do REQUEST__MODAL_SHOW.
     */
    _handleRequestModalShowImportant(options)
    {
        var $modalEl = $('#modal-generic');
        if ($modalEl.is(':visible'))
        {
            $('.modal-footer').text(options.title + ': ' + options.content);
            $('.modal-footer').removeClass('modal-footer-error');
        }
        else
        {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, options);
        }
        $('.modal-dialog').addClass('modal-fit');
        $('.modal-footer').removeClass('modal-footer-error');
    }

    /**
     * Handles modal error. If modal is already visible, changes footer text.
     * Else, creates simple modal.
     */
    _handleRequestModalError(options)
    {
        var $modalEl = $('#modal-generic');
        if ($modalEl.is(':visible'))
        {
            $('.modal-footer').text(options.content);
        }
        else
        {
            Radio.channel('rodan').request(RODAN_EVENTS.REQUEST__MODAL_SHOW, {title: options.title || 'Error', content: options.content});
        }
        $('.modal-footer').addClass('modal-footer-error');
    }
}
