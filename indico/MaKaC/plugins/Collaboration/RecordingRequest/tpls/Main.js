{
    checkParams : function () {
        return {
        }
    },

    errorHandler: function(event, error) {
        if (error.operation == "create") {
            CSErrorPopup($T("Could not send email to responsible"),
                         [Html.span("", $T("There was a problem when sending the notification email to the Recording responsible:"), Html.br(), error.inner)])
        }
        if (error.operation == "edit") {
            CSErrorPopup($T("Could not send email to responsible"),
                         [Html.span("", $T("There was a problem when sending the notification email to the Recording responsible:"), Html.br(), error.inner)])
        }
        if (error.operation == "remove") {
            CSErrorPopup($T("Could not send email to responsible"),
                        [Html.span("", $T("There was a problem when sending the notification email to the Recording responsible:"), Html.br(), error.inner)])
        }
    },

    customText : function(booking) {
        if (booking.acceptRejectStatus === false && trim(booking.rejectReason)) {
            return $T("Rejection reason: ") + trim(booking.rejectReason);
        }
    },

    clearForm : function () {
        var formNodes = IndicoUtil.findFormFields($E('RecordingRequestForm'));
        IndicoUtil.setFormValues(formNodes, {'numRemoteViewers':'', 'numAttendees':'', 'otherComments':''});
        if (!isLecture) {
            $E('allTalksRB').dom.checked = true;
            IndicoUI.Effect.disappear($E('contributionsDiv'));
        }
        $E('postingUrgency').dom.value = "withinWeek";
    },

    onLoad : function() {
        RRUpdateContributionList();

        IndicoUtil.enableDisableForm($E("RRForm"), RRRecordingCapable);

        if (!isLecture) {
            if (singleBookings['RecordingRequest'] && singleBookings['RecordingRequest'].bookingParams.talks == 'choose') {
                IndicoUI.Effect.appear($E('contributionsDiv'));
            }
        }

        if(!singleBookings['RecordingRequest']) {
            callFunction('RecordingRequest', 'clearForm');
        }
    }
}
