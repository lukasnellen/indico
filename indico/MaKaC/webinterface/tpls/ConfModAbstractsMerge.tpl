<form action=${ postURL } method="POST">
    <table width="60%" align="center" border="0" style="border-left: 1px solid #777777">
        <tr>
            <td class="groupTitle" colspan="2"> ${ _("Merging abstracts")}</td>
        </tr>
        <tr>
            <td bgcolor="white">
                <table width="100%">
                    ${ errorMsg }
                    <tr>
                        <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("Abstract ids to be merged")}</span></td>
                        <td>
                            <input type="text" size="60" name="selAbstracts" value=${ selAbstracts }>
                        </td>
                    </tr>
                    <tr>
                        <td nowrap class="titleCellTD"><span class="titleCellFormat"> ${ _("Target abstract id")}</span></td>
                        <td>
                            <input type="text" name="targetAbstract" value=${ targetAbs }>
                        </td>
                    </tr>
                    <tr>
                        <td></td>
                        <td nowrap>
                            <input type="checkbox" name="includeAuthors"${ inclAuthChecked }><font color="gray"> ${ _("Include authors in target abstract")}
                        </td>
                    </tr>
                    <tr>
                        <td align="center" colspan="2">
                            <input type="checkbox" name="notify"${ notifyChecked }><font color="gray"> ${ _("Automatic email notification")}</font>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    <tr>
                        <td colspan="2" class="titleCellFormat"> ${ _("Comments")}<br>
                            <textarea name="comments" cols="70" rows="5">${ comments }</textarea>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td colspan="2">&nbsp;</td>
        </tr>
        <tr>
            <td colspan="2" align="center">
                <input type="submit" class="btn" name="OK" value="${ _("submit")}">
                <input type="submit" class="btn" name="CANCEL" value="${ _("cancel")}">
            </td>
        </tr>
    </table>
</form>
