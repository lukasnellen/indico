<%page args="repeatability=None, form=None, unavailableDates=None"/>
<script type="text/javascript">

    // Comments the repeatition for user, to make it clear
    function set_repeatition_comment() {
        var s = '';
        var repType = parseInt($('#repeatability').val(), 10);
        if(repType > 0) {
            var date = new Date(parseInt($('#sYear').val(), 10), parseInt($('#sMonth').val()-1, 10), parseInt($('#sDay').val(), 10));
            var weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            s = 'on ' + weekDays[date.getDay()];
            if(repType == 4) {
                weekNr = Math.floor( date.getDate() / 7 ) + 1;
                postfix = ['st', 'nd', 'rd', 'th', 'th'];
                weekNrStr = 'the ' + weekNr + postfix[weekNr-1] + ' ';
                s = 'on ' + weekNrStr + weekDays[date.getDay()] + ' of a month';
            }
        }
        $('#repComment').html(s);
    }

    IndicoUI.executeOnLoad(function()
    {
        var startDate = IndicoUI.Widgets.Generic.dateField_sdate(false,null,['sDay', 'sMonth', 'sYear']);
        $E('sDatePlace').set(startDate);

        var endDate = IndicoUI.Widgets.Generic.dateField_edate(false,null,['eDay', 'eMonth', 'eYear']);
        $E('eDatePlace').set(endDate);

        /* In case the date changes, we need to check whether the start date is greater than the end date,
        and if it's so we need to change it */
        startDate.observe(function(value) {
            if ( IndicoUtil.parseDate(startDate.get()) > IndicoUtil.parseDate(endDate.get()) ) {
                endDate.set(startDate.get());
                endDate.dom.onchange();
                set_repeatition_comment();
            }
        });

        endDate.observe(function(value) {
            if ( IndicoUtil.parseDate(startDate.get()) > IndicoUtil.parseDate(endDate.get()) ) {
                startDate.set(endDate.get());
                startDate.dom.onchange();
                set_repeatition_comment();
            }
        });

       % if startDT.day != '':
            startDate.set('${ startDT.day }/${ startDT.month }/${ startDT.year }');
        % endif

        % if endDT.day != '':
            endDate.set('${ endDT.day }/${ endDT.month }/${ endDT.year }');
        % endif

     });
</script>
                                        % if unavailableDates:
                                        <tr id="sdatesTR" >
                                            <td class="subFieldWidth" align="right" valign="top" ><small>${ _("Unavailability") }</small></td>
                                            <td class="blacktext">
                                            <span style="color:#881122">${ _("This room cannot be booked during the following dates due to maintenance reasons") }:<ul><li>${ "</li><li>".join(map(lambda x: 'from %s to %s'%(x.getStartDate().strftime('%d/%m/%Y'), x.getEndDate().strftime('%d/%m/%Y')), unavailableDates )) }</li></ul></span>
                                            </td>
                                        </tr>
                                        % endif
                                        <tr id="sdatesTR" >
                                            <td class="subFieldWidth" align="right" ><small> ${ _("Start Date")}&nbsp;&nbsp;</small></td>
                                            <td class="blacktext">
                                                <span id="sDatePlace"></span>
                                                <input type="hidden" value="${ startDT.day }" name="sDay" id="sDay"/>
                                                <input type="hidden" value="${ startDT.month }" name="sMonth" id="sMonth"/>
                                                <input type="hidden" value="${ startDT.year }" name="sYear" id="sYear"/>
                                            </td>
                                          </tr>
                                         <tr id="edatesTR" >
                                            <td class="subFieldWidth" align="right" ><small> ${ _("End Date")}&nbsp;&nbsp;</small></td>
                                            <td>
                                                <span id="eDatePlace"></span>
                                                <input type="hidden" value="${ endDT.day }" name="eDay" id="eDay"/>
                                                <input type="hidden" value="${ endDT.month }" name="eMonth" id="eMonth"/>
                                                <input type="hidden" value="${ endDT.year }" name="eYear" id="eYear"/>
                                            </td>
                                        </tr>
                                        <tr id="hoursTR" >
                                            <td align="right" ><small> ${ _("Hours")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="blacktext">
                                                <input name="sTime" id="sTime" maxlength="5" size="5" type="text" value="${ startT }" onchange="" /> &nbsp;&mdash;&nbsp;
                                                <input name="eTime" id="eTime" maxlength="5" size="5" type="text" value="${ endT }" onchange="" />
                                                <span id="holidays-warning" style="color: Red; font-weight:bold;"></span>
                                            </td>
                                        </tr>
                                        <tr id="repTypeTR" >
                                            <td align="right" ><small> ${ _("Type")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="blacktext" >
                                                <select name="repeatability" id="repeatability" onchange="set_repeatition_comment();">
                                                <% sel = [ "", "", "", "", "", "" ]; %>
                                                % if repeatability == None:
                                                <%     sel[5] = 'selected="selected"' %>
                                                % endif
                                                % if repeatability != None:
                                                <%     sel[repeatability] = 'selected="selected"' %>
                                                % endif
                                                    <option ${ sel[5] } value="None"> ${ _("Single day")}</option>
                                                    <option ${ sel[0] } value="0"> ${ _("Repeat daily")}</option>
                                                    <option ${ sel[1] } value="1"> ${ _("Repeat once a week")}</option>
                                                    <option ${ sel[2] } value="2"> ${ _("Repeat once every two weeks")}</option>
                                                    <option ${ sel[3] } value="3"> ${ _("Repeat once every three weeks")}</option>
                                                    <option ${ sel[4] } value="4"> ${ _("Repeat every month")}</option>
                                                </select>
                                                <span id="repComment" style="margin-left: 12px"></span>
                                                ${contextHelp('repeatitionHelp' )}
                                            </td>
                                        </tr>
