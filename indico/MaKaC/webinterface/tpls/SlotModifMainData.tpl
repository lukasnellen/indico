<form id="slotModificationForm" action="${ postURL }" method="POST">
    <table width="60%" align="center" border="0" style="border-left: 1px solid #777777;padding-left:2px">
        <tr>
            <td colspan="2" class="groupTitle"> ${ _("Edit slot")}</td>
        </tr>
        <tr>
            <td colspan="2">${ errors }</td>
        </tr>
        <tr>
            <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("Title")}</span></td>
            <td bgcolor="white" width="100%">
        <input type="text" size="60" name="title" value="${ title }">
        </td>
        </tr>

        <%include file="EventLocationInfo.tpl" args="event=self_._rh._slot, modifying=True, parentRoomInfo=roomInfo(self_._rh._slot, level='inherited') ,showParent=True, conf = False"/>

        <tr>
            <td class="titleCellTD"><span class="titleCellFormat"> ${ _("Start date")}</span></td>
            <td valign="top" bgcolor="white" width="100%">&nbsp;
                <input type="text" size="2" name="sDay" value=${ sDay } onChange="this.form.eDay.value=this.value;">-
                <input type="text" size="2" name="sMonth" value=${ sMonth } onChange="this.form.eMonth.value=this.value;">-
                <input type="text" size="4" name="sYear" value=${ sYear } onChange="this.form.eYear.value=this.value;">
                <input type="image" src=${ calendarIconURL } alt="open calendar" border="0" onClick="javascript:window.open('${ calendarSelectURL }?daystring=sDay&monthstring=sMonth&yearstring=sYear&month='+this.form.sMonth.value+'&year='+this.form.sYear.value+'&date='+this.form.sDay.value+'-'+this.form.sMonth.value+'-'+this.form.sYear.value,'calendar','scrollbars=no,menubar=no,width=200,height=170');return false;">
                <input type="text" size="2" name="sHour" value=${ sHour }>:
                <input type="text" size="2" name="sMinute" value=${ sMinute }>
        ${ autoUpdate }
        &nbsp<input type="checkbox" name="move" value="1"> Move timetable content
            </td>
        </tr>
        <tr>
            <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("End time")}</span></td>
            <td bgcolor="white" width="100%">&nbsp;
                <input type="hidden" name="eDay" value="${ eDay }">
                <input type="hidden" name="eMonth" value="${ eMonth }">
                <input type="hidden" name="eYear" value="${ eYear }">
                <input type="text" size="2" name="eHour" value="${ eHour }">:
                <input type="text" size="2" name="eMinute" value="${ eMinute }">
            </td>
        </tr>
        <tr>
            <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("Contribution duration")}</span></td>
            <td bgcolor="white" width="100%">&nbsp;
                <input type="text" size="2" name="contribDurHours" value="${ contribDurHours }">:
                <input type="text" size="2" name="contribDurMins" value="${ contribDurMins }">
            </td>
        </tr>
        <tr>
            <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("Conveners")}</span></td>
            <td>
                <table cellspacing="0" cellpadding="0" width="50%" align="left" valign="middle" border="0">
                    ${ conveners }
                    <tr>
                        <td colspan="3" nowrap>&nbsp;
                            <input type="submit" class="btn" name="remConveners" value="${ _("remove selected convener")}">
                            <input type="submit" class="btn" name="addConvener" value="${ _("new convener")}">
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr align="center">
            <td colspan="2" class="buttonBar" valign="bottom" align="center">
        <input type="submit" class="btn" name="OK" value="${ _("ok")}">
        <input type="submit" class="btn" value="cancel" name="${ _("cancel")}">
            </td>
        </tr>
    </table>
</form>


<script type="text/javascript">
  injectValuesInForm($E('slotModificationForm'));
</script>
