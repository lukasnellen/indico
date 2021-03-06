<div style="padding:20px 0px">

<a href="${urlHandlers.UHConfAbstractBook.getURL(conf)}">${_("Download book of abstracts")}</a>

<div style="margin-top: 10px;">
% if bookOfAbstractsActive:
    % if bookOfAbstractsMenuActive:
        ${ _("Users will be able to download the book from the <a href='%s'>event home page</a>. You can disable the download from the <a href='%s'>Layout->Menu</a> configuration page.") % (urlHandlers.UHConferenceDisplay.getURL(conf), urlHandlers.UHConfModifDisplayMenu.getURL(conf))}
    % else:
        ${ _("Note that you need to enable the book of abstracts link in <a href='%s'>Layout->Menu</a>") % urlHandlers.UHConfModifDisplayMenu.getURL(conf) }.
    % endif
% else:
    ${ _("Note that you need to enable call for abstracts if you wish to provide a link in the <a href='%s'>event home page</a> menu, so users can download your book of abstracts")% urlHandlers.UHConferenceDisplay.getURL(conf) }.
% endif
</div>
</div>

<div class="groupTitle">${ _("Customisation")}</div>
<table width="90%" align="center" border="0">
    <tr>
        <td class="dataCaptionTD"><span class="dataCaptionFormat"> ${ _("Additional text")}</span></td>
        <td>
            <div class="blacktext" id="inPlaceEditAdditionalText">${ text }</div>
        </td>
    </tr>
    <tr>
        <td class="dataCaptionTD"><span class="dataCaptionFormat"> ${ _("Sort by")}</span></td>
        <td class="blacktext" width="100%">
            <div id="inPlaceEditSortBy" style="display:inline"></div>
        </td>
    </tr>
    <tr>
        <td class="dataCaptionTD">
            <span class="dataCaptionFormat"> ${ _("Miscellaneous options")}</span><br/><br/>
            <img src="${Config.getInstance().getSystemIconURL( 'enabledSection' )}" alt="${ _("Click to disable")}"> <small> ${ _("Enabled option")}</small>
            <br />
            <img src="${Config.getInstance().getSystemIconURL( 'disabledSection' )}" alt="${ _("Click to enable")}"> <small> ${ _("Disabled option")}</small>
            <br />
        </td>
        <td bgcolor="white" width="100%" class="blacktext">
            % if showIds:
                <% icon = str(Config.getInstance().getSystemIconURL( "enabledSection" )) %>
            % else:
                <% icon = str(Config.getInstance().getSystemIconURL( "disabledSection" )) %>
            % endif
            <a href="${urlToogleShowIds}"><img src="${icon}"> ${_("Show Abstract IDs")}</a> ${_("(Table of Contents)")}
            <br/>
        </td>
    </tr>
</table>
<script type="text/javascript">

<%  from MaKaC.common import info %>
$E('inPlaceEditAdditionalText').set(new RichTextInlineEditWidget('abstract.abstractsbook.changeAdditionalText', ${ jsonEncode(dict(conference="%s"%conf.getId())) }, ${ jsonEncode(text) }, 300, 45, "${_('No additional text')}").draw());
new IndicoUI.Widgets.Generic.selectionField($E('inPlaceEditSortBy'), 'abstract.abstractsbook.changeSortBy', ${dict(conference="%s"%conf.getId())}, ${sortByList|n,j}, '${sortBy}');
</script>


