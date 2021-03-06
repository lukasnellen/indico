<%page args="room=None"/>
                              <!-- ROOM -->
                              <tr>
                                <td class="titleUpCellTD"><span class="titleCellFormat"> ${ _("Room")}</span></td>
                                <td>
                                    <table width="100%">
                                        <tr>
                                            <td class="subFieldWidth" align="right" valign="top"><small> ${ _("Name")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="blacktext"><a href="${ roomDetailsUH.getURL( room ) }">${ room.building }-${ room.floor }-${ room.roomNr }
                                                % if room.name != str(room.building) + '-' + str(room.floor) + '-' + str(room.roomNr):
                                                    <small>(${ room.name })</small>
                                                 % endif
</a>
                                            </td>
                                        </tr>
                                        % if room.photoId != None:
                                        <tr>
                                            <td class="subFieldWidth" align="right" valign="top"><small> ${ _("Interior")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="thumbnail">
                                                <a href="${ room.getPhotoURL() }" rel="lightbox" title="${ room.photoId }">
                                                    <img border="1px" src="${ room.getSmallPhotoURL() }" alt="${ str( room.photoId ) }"/>
                                                </a>
                                            </td>
                                        </tr>
                                        % endif
                                        <tr>
                                            <td class="subFieldWidth" align="right" valign="top"><small> ${ _("Room key")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="blacktext">${ room.whereIsKey }${contextHelp('whereIsKeyHelp' )}</td>
                                        </tr>
                                        % if room.comments:
                                        <tr>
                                            <td class="subFieldWidth" align="right" valign="top"><small> ${ _("Comments")}&nbsp;&nbsp;</small></td>
                                            <td align="left" class="blacktext">${ room.comments }</td>
                                        </tr>
                                        % endif
                                    </table>
                                </td>
                              </tr>
