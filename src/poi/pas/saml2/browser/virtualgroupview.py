# -*- coding: utf-8 -*-
from Products.Five import BrowserView
# from poi.main_dexterities.interfaces import ICountry
from poi.pas.saml2.interfaces import DEFAULT_ID_USERS
from plone import api
from Products.CMFPlone.utils import safe_unicode
import datetime
from string import join
import logging

logger = logging.getLogger("Plone")
"""  --> userdata
{
    'Person.Gender': [u '1'],
    'group': set([u 'hu00201']),
    'Organization.ID': [u '47017'],
    'userid': '104323',
    'PartnerKey.Brand': [u 'C'],
    'secret': 'xxxxxxxxxxxxxxxxxxxxxxxx',
    'PartnerKey.PartnerNumber': [u '00201'],
    'Person.LastName': [u 'Tank\xf3'],
    'Portal.ID': [u 'HU'],
    'Person.Email': [u 'tankojozsef@gmail.com'],
    'PartnerKey.Country': [u 'HU'],
    'Person.Roles': [u 'FU_F_ALAPFUNKCIO', u 'TA_T_HDL_SCHULUNG', u 'TA_T_HDL_STD', u 'TA_ALL', u 'TA_T_HDL_INETWTG'],
    'Person.FirstName': [u 'J\xf3zsef']
}
"""

class Saml2GroupView(BrowserView):
    def showgroupform(self):

        import pdb
        pdb.set_trace()

        #print '===>',self.Countrysel
        userid = ''
        dlrid = ''
        username = ''
        prefix = 'at'
        table = []
        # ------------------------------------
        # Check Request
        # ------------------------------------
        if hasattr(self.request, 'userid'):
            userid = getattr(self.request, 'userid')
        elif hasattr(self.request, 'hdlid'):
            dlrid = getattr(self.request, 'hdlid')
            dlrid = '00000' + dlrid
            dlrid = dlrid[len(dlrid) - 5:]
            if self.Countrysel.id == 'at': prefix = 'a'
            else: prefix = self.Countrysel.id
            #dlrid = prefix + dlrid
            #print '==>',dlrid,prefix
        elif hasattr(self.request, 'usrname'):
            username = getattr(self.request, 'usrname')
        else:
            userid = '-'

        plugin = api.portal.get_tool('acl_users')[DEFAULT_ID_USERS]
        portal = api.portal.get()
        BigCountry = self.Countrysel.id.upper()

        # ---------------------------------------------------
        # Show single User
        # ---------------------------------------------------
        if userid != '' and userid != '-':
            # print 'Wir Starten mit User',userid
            userdata = plugin._userdata_by_userid.get(userid, None)
            table.append('<div class="box"><table>')
            if hasattr(userdata, 'data'):
                for i in userdata:
                    table.append('<tr><td>' + str(i) + '</td><td>' + str(userdata[i]) + '</td></tr>')
            table.append('</table></div>')

        # ---------------------------------------------------
        # Show all user of dealer-group
        # ---------------------------------------------------
        elif dlrid != '' and dlrid != '-':
            # print 'Wir Starten mit',dlrid
            userTable = []
            for zhl in range(1, 10):
                sid = str(zhl)
                test = plugin.enumerateUsers(sid, exact_match=False)
                for usr in test:
                    userdata = plugin._userdata_by_userid.get(usr["id"], None)
                    # print userdata["PartnerKey.PartnerNumber"]
                    if hasattr(userdata, 'data'):
                        # dealernumbers from country only
                        if userdata["PartnerKey.PartnerNumber"][0] == dlrid and BigCountry == userdata["Portal.ID"][0]:
                            userTable.append(userdata)
                            #print usr["id"], usr["pluginid"]
                    else:
                        continue
                # print usr["id"],usr["pluginid"]



            table.append('<div class="box" style="text-align: right;">RoleMap: D=Dealer, J=Jobs, C=Country, M=Manager, S=Support</div>')
            table.append(
                '<div class="box"><table><tr><th>Hdl-Nr</th><th>Nachname</th><th>Vorname</th><th>ID</th><th>Key</th><th>Role-Mapping</th></tr>')

            for userdata in userTable:
                LastName = safe_unicode(userdata["Person.LastName"][0])
                FirstName = safe_unicode(userdata["Person.FirstName"][0])
                MyRole = self.getroles(userdata)
                table.append('<tr><td><a href="#" onclick="SetLogin('+"'"+str(userdata["userid"])+"','"+str(userdata["secret"]) +
                    "','"+str(userdata["PartnerKey.PartnerNumber"][0]) + "','" + MyRole +
                    "')"+'">' + str(userdata["PartnerKey.PartnerNumber"][0]) + '</td><td>' + LastName + '</td><td>' + FirstName + '</td>')
                table.append('<td>' + str(userdata["userid"]) + '</td><td>' + str(userdata["secret"])  + '</td><td>' +MyRole+ '</td></tr>')
            table.append('</table></div>')
        # ---------------------------------------------------
        # Show all user of dealer-group
        # ---------------------------------------------------
        elif username != '' and username != '-':
            print 'Wir Starten mit', username
            userTable = []
            for zhl in range(1, 10):
                sid = str(zhl)
                test = plugin.enumerateUsers(sid, exact_match=False)
                for usr in test:
                    userdata = plugin._userdata_by_userid.get(usr["id"], None)
                    # print userdata["PartnerKey.PartnerNumber"]
                    if hasattr(userdata, 'data'):
                        if safe_unicode(username) in safe_unicode(userdata["Person.LastName"][0]):
                            userTable.append(userdata)
                            # print usr["id"],usr["pluginid"]
                            #print userdata["Person.Roles"]
                    else:
                        continue
                # print usr["id"],usr["pluginid"]
            table.append('<div class="box" style="text-align: right;">RoleMap: D=Dealer, J=Jobs, C=Country, M=Manager, S=Support</div>')
            table.append(
                '<div class="box"><table><tr><th>Hdl-Nr</th><th>Nachname</th><th>Vorname</th><th>ID</th><th>Key</th><th>Role-Mapping</th></tr>')

            for userdata in userTable:
                LastName = safe_unicode(userdata["Person.LastName"][0])
                FirstName = safe_unicode(userdata["Person.FirstName"][0])
                MyRole = self.getroles(userdata)
                table.append('<tr><td><a href="#" onclick="SetLogin('+"'"+str(userdata["userid"])+"','"+str(userdata["secret"]) +
                    "','"+str(userdata["PartnerKey.PartnerNumber"][0]) + "','" + MyRole +
                    "')"+'">' + str(userdata["PartnerKey.PartnerNumber"][0]) + '</td><td>' + LastName + '</td><td>' + FirstName + '</td>')
                table.append('<td>' + str(userdata["userid"]) + '</td><td>' + str(userdata["secret"])  + '</td><td>' +MyRole+ '</td></tr>')
            table.append('</table></div>')
        return join(table, '\n')


    def getroles(self, userdata):
        SAMLROLE_TO_GROUP = {
            u'TA_T_HDL_INETWTG': 'D',
            u'T_INTERNETW': 'D',
            u'S_HDL_INETWTG': 'D',
            u'FU_F_GF': 'D',
            u'FU_GESCHFUEHR_ASIST': 'D',
            u'FU_GESCHFUEHR_NACHF': 'D',
            u'FU_GF2': 'D',
            u'TA_HI_SUP': 'S',
            u'FU_HI_SUP': 'S',
            u'TA_HDL_WEB_BETR': 'J',
            #'TA_HDL_WEB_BETR': 'D',
            u'TA_T_GH_INETWTG': 'C',
            u'TA_HI_ENTW': 'M',
            u'FU_HI_ENTW': 'M'
        }

        Rset = {}
        for role_key in userdata["Person.Roles"]:
            if role_key in SAMLROLE_TO_GROUP:
                Kennzeichen = SAMLROLE_TO_GROUP[role_key]
                Rset[Kennzeichen] = '-'
        MyRole = ''
        for xd in Rset:
            MyRole = MyRole+xd
        return MyRole


    def stoprint(self, zw):

        for attr in zw:
            if attr.startswith('_'): continue
            if attr.startswith('workflow_'): continue
            inhalt = zw[attr]
            if isinstance(inhalt, datetime.date):
                continue
            elif isinstance(inhalt, str):
                if len(inhalt) > 80: inhalt = inhalt[0:80] + '...'
                # inhalt = safe_unicode(inhalt)
                print attr, inhalt

    #---------------------------------------------------
    # Get Country Site
    #---------------------------------------------------
    def getCountry(self,context):
        for item in context.aq_chain:
            # TODO if ICountry.providedBy(item):
            print "fix ze this one"
            return item,True
        return context,False

    def __call__(self):
        self.Countrysel,ok = self.getCountry(self.context)
        return super(Saml2GroupView, self).__call__()
