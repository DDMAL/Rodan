$(document).ready(function () {
    // The search box
    $('#search').submit(function () {
        var query = $('#search-query').val().toLowerCase();
        var numResults = 0;
        // Hide all the projects that don't have the search term in their name/desc
        $('#project-list').find('a').each(function () {
            var projectName = $(this).text().toLowerCase();
            var projectDesc = $(this).attr('title').toLowerCase();
            if (projectName.indexOf(query) + projectDesc.indexOf(query) === -2) {
                // Not present in either the name or the description; hide
                $(this).hide();
            } else {
                $(this).show();
                numResults++;
            }
        });

        var resultsText = numResults + ' result' + ((numResults === 1) ? '' : 's');
        $('#results-tab').show().addClass('active').text(resultsText);
        $('#title-tab').removeClass('active');
        return false;
    });

    $('#title-tab').click(function () {
        if (!$('#results-tab').is(':hidden')) {
            $('#results-tab').removeClass('active').hide();
            $(this).addClass('active');
            // Show all the project lis
            $('#project-list').find('a').each(function () {
                $(this).show();
            });
        }
    });

    $(function() {
        $( "#upload-images" ).sortable({
            update: function (event, ui) {
                var currentIndex = ui.item.index();
                var pageID = ui.item.attr("data-page");
                var inputPageID= $("<input>").attr("type", "hidden").attr("name", "page-id").val(pageID);
                var inputPageSeq = $("<input>").attr("type", "hidden").attr("name", "page-sequence-new").val(currentIndex + 1);
                $("form").append($(inputPageID));
                $("form").append($(inputPageSeq));
                $("form").submit();
            }
        });
        $( "#upload-images" ).disableSelection();
    });

    $('#job-lists').delegate('.edit-parameters', 'click', function (event) {
        var jobSlug = $(this).parent().attr('data-id');
        $('#job-to-edit').val(jobSlug);
        $('#job-form').submit();
    });

    $('#job-form').submit(function () {
        var jobsList = [];
        $('#workflow-jobs').children().each(function () {
            jobsList.push($(this).attr('data-id'));
        });

        $('#ordered-jobs').val(jobsList.join(' '));
    });

    $('#workflows').delegate('.remove-workflow', 'click', function (event) {
        var jobNode = $(this).parent().parent();
        // The input type is the same as the previous job's output type
        var workflow_id = jobNode.attr('workflow-id');

        $('#workflow-to-remove').val(workflow_id);
        $('#form').submit();
        return false;
    });

    $('#workflow-jobs').delegate('.remove-job', 'click', function (event) {
        var jobNode = $(this).parent().parent();
        // The input type is the same as the previous job's output type
        var jobSeqIndex = jobNode.attr('sequence-index');

        $('#job-to-remove').val(jobSeqIndex);
        $('#form').submit();
        return false;
    });

    $('#available-jobs').delegate('.add-job', 'click', function (event) {
        var jobNode = $(this).parent().parent();
        var jobID = jobNode.attr('data-id');

        $('#job-to-add').val(jobID);
        $('#form').submit();
        return false;
    });

    // If the flash message exists, make it disappear after some time
    // and also refresh the page
    if ($('.flash-message').length) {
        setTimeout(function () {
            $('.flash-message').fadeOut('slow');
        }, 2000);
    }

    // Handle selecting pages (the add pages view)
    $('.select-pages').click(function () {
        // Odd and even seem to be switched but it's just because it's 0-indexed
        var filter = $(this).attr('data-filter');
        $('.image-buttons img').filter(filter).each(function () {
            $(this).addClass('selected');
            $(this).next().prop('checked', true);
        });

        $('.image-buttons img').not(filter).each(function () {
            $(this).removeClass('selected');
            $(this).next().prop('checked', false);
        });
    });

    var submitForm = $('#upload-images').length;
    // If the .image-buttons class exists, handle clicking the images
    if ($('.image-buttons').length) {
        $('.image-buttons').delegate('img', 'click', function (event) {
            // Check the radio button immediately following the image
            var radioButton = $(this).next();
            if (radioButton.attr('checked')) {
                radioButton.prop('checked', false);
            } else {
                radioButton.prop('checked', true);
            }

            if (submitForm) {
                $('#form').submit();
            } else {
                $(this).toggleClass('selected');
            }
        });
    }

    // If file uploading is present, hide the submit button submit automatically
    if ($('input[type=file]').length) {
        $('.submit').hide();

        $('input[type=file]').change(function (e) {
            var files = e.target.files;
            
            if ($('#page-placeholder').length) {
                $('#page-placeholder').remove();
            }

            // Show a modal dialog until the uploading is complete
            $('#modal').show();

            $('#form').trigger('submit');
        });
    }

 // Does not trigger if a fake-img is added dynamically (intended behaviour)
    if ($('.fake-img').length) {
        var imageInterval = setInterval(function () {
            if (!$('.fake-img').length) {
                clearInterval(imageInterval);
            } else {
                var pageID = $('.fake-img').attr('data-page');
                $.ajax({
                    cache: false,
                    url: '/status/page/' + pageID,
                    context: $('.fake-img'),
                    success: function (pageStatus) {
                        if (pageStatus) {
                            this.attr('class', 'page-loading-done');
                            var image = this.find('img');
                            $.each(image, function(index, element){
                                // Must be after image is ready, to prevent caching
                               $(element).attr('src', $(element).attr('data-src'));
                                
                                // Change the "X pages still processing" text
                                // Assumes only one page is processing ... fix later
                                // Also results in awkward pluralisation for "page"
                                $('#num-processing').text('no');
                            });
                        }
                    },
                });
            }
        }, 1000);
    }

    var tickables = {};

    var updateTickables = function () {
        var tickInterval = setInterval(function () {
            var element, oldText, newText;
            for (resultID in tickables) {
                element = tickables[resultID];
                oldText = element.textContent;
                newText = parseInt(oldText, 10) + 1;
                element.textContent = newText;
            }

            $.ajax({
                cache: false,
                url: '/status/task',
                data: {
                    result_ids: _.keys(tickables)
                },
                success: function (statuses) {
                    for (resultID in statuses) {
                        var taskStatus = statuses[resultID];
                        var element = tickables[resultID];
                        if (taskStatus == -1) {
                            // Add a "done" thing
                            $(element).parent().append(' - FAILED! You probably have to redo the binarisation process.');
                            // Pause the ticking
                            delete tickables[resultID];

                            // Then refresh the page (temp solution)
                            setTimeout(function () {
                                location.search = '';
                            }, 2000);
                        } else if (taskStatus == 1) {
                            // Add a "done" thing
                            $(element).parent().append(' - DONE (will autorefresh shortly)');
                            // Pause the ticking
                            delete tickables[resultID];

                            // Then refresh the page (temp solution)
                            setTimeout(function () {
                                location.search = '';
                            }, 2000);
                        }
                    }
                }
            });
        }, 1000);
    };

    if ($('.tick').length) {
        $('.tick').each(function (index, element) {
            var resultID = $(element).attr('data-result-id');
            tickables[resultID] = element;
        });

        updateTickables();
    }
});
