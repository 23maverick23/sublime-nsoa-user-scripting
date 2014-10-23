from datetime import datetime
import itertools
import json
import os
import re
import xml.etree.ElementTree as ET
import webbrowser

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

import sublime
import sublime_plugin


## ----------------------------- GLOBAL CONSTANTS ----------------------------------------------- ##
ST3 = sublime.version() >= '3000'

DEFAULT_WSDL_URL = 'http://www.openair.com/wsdl.pl?wsdl'
XML_XS = '{http://www.w3.org/2001/XMLSchema}'

SOAP_GUIDE_URL = 'http://www.openair.com/download/NetSuiteOpenAirSOAPAPIGuide.pdf'
SCRIPTING_GUIDE_URL = 'http://www.openair.com/download/NetSuiteOpenAirUserScriptingGuide.pdf'
SCRIPTING_REFERENCE_URL = 'http://www.openair.com/download/NetSuiteOpenAirUserScriptingReferenceCard.pdf'

## ----------------------------- CONTEXT MENU DEFAULTS ------------------------------------------ ##

CONTEXT_MENU_DEFAULT = '''
[
    {
        "caption": "NSOA",
        "id": "nsoa-context-main",
        "children": [
            {
                "caption": "View WSDL Data...",
                "id": "nsoa-context-special",
                "children": []
            }
        ]
    }
]
'''

CONTEXT_MENU_DEFAULT_OLD = '''
[
    {
        "caption": "-",
        "id": "nsoa-context-separator-top"
    },
    {
        "caption": "NSOA",
        "id": "nsoa-context-main",
        "children": [
            {
                "caption": "View WSDL content...",
                "id": "nsoa-context-wsdl",
                "children": []
            }
        ]
    },
    {
        "caption": "-",
        "id": "nsoa-context-separator-bottom"
    }
]
'''

## ---------------------------------------------------------------------------------------------- ##


class NsoaGenerateWsdlBase(sublime_plugin.WindowCommand):
    """
    A Sublime window command base class for loading WSDL files.

    """
    def get_package_file_path(self, path_list):
        """
        Gets the path to the file or folder specified. Expects
        a list of path directories.

        ex// ['NSOA', 'completions', 'Wsdl.sublime-completions']

        """
        try:
            file_path = os.path.join(*path_list)
            # location if added manually to sublime text
            packages_path = os.path.join(sublime.packages_path(), file_path)

            if sublime.platform() == 'windows':
                packages_path = packages_path.replace('\\', '/')

            if os.path.exists(packages_path):
                return packages_path
            else:
                sublime.error_message("Unable to find '{0}' in your Sublime packages directory.".format(file_path))
                return None
        except Exception as e:
            print(e)
            return None

    def validate_url(self, url):
        """
        Validates the url against knows URL configurations
        Regex example: http://regex101.com/r/oK1eY1/1

        """
        status = []
        try:
            p = re.compile('^(?P<protocol>http(?:s)?)://'                   # match protocol
                           '(?P<subdomain>www|sandbox|demo|qa)'             # match subdomain
                           '\.openair(?:1)?\.com(?:\:)?(?P<port>\d+)?'      # match domain/port
                           '(?:|\/)/(?:wsdl\.pl\?)?(?P<wsdl>wsdl|\w+)?$',   # match url end
                           re.MULTILINE)
            m = re.match(p, url)
            s = {}
            s['code'] = 0 if m else 1
            s['data'] = m.groupdict() if m else {}
            s['url'] = url
            status.append(s)
        except Exception as e:
            print(e)
        finally:
            return status

    def sort_list_dict(self, field_list, dictkey):
        """
        Returns a list, sorted by a dictionary key value,
        and case insensitive.

        """
        return sorted(field_list, key=lambda x: x[dictkey].lower())

    def sort_list(self, field_list):
        """
        Returns a list, sorted case insensitive.

        """
        return sorted(field_list, key=str.lower)

    def create_context_menu(self):
        """
        Create a context menu using WSDL settings.

        """
        settings = sublime.load_settings('NSOA.sublime-settings')
        # NOTE: Moving the context menu to the User directory
        context_path_list = ['User', 'NSOA', 'Context.sublime-menu']
        # context_path = self.get_package_file_path(context_path_list)
        context_path = os.path.join(sublime.packages_path(), os.path.join(*context_path_list))

        if not os.path.exists(os.path.dirname(context_path)):
            os.makedirs(os.path.dirname(context_path))

        sublime_context_json = json.loads(CONTEXT_MENU_DEFAULT)
        wsdl_json = json.loads(settings.get('wsdl_json'))

        # the last array index should match the 'nsoa-context-wsdl' context item
        context_root = sublime_context_json[0]['children'][0]
        del context_root['children'][:]

        # First Iteration: create alphabetized menu
        alpha_set = set()
        alpha_list = []
        for complexname in wsdl_json:
            alpha_set.add(complexname[2])
            alpha_list.append(complexname)

        alpha_set_sorted = self.sort_list(alpha_set)
        alpha_list_sorted = self.sort_list(alpha_list)
        alpha_set_keys = {}
        alpha_list_keys = {}

        for num, letter in enumerate(alpha_set_sorted):
            context_alpha = {"caption": "{0}".format(letter), "children": []}
            context_root['children'].append(context_alpha)
            alpha_set_keys[letter] = num

        for k, g in itertools.groupby(alpha_list_sorted, key=lambda x: x[2]):
            alpha_list_keys[k] = {key: value for (value, key) in enumerate(list(g))}

        # Second Interation: add complex types and fields
        for complexname in alpha_list_sorted:
            _lvl = alpha_set_keys[complexname[2]]  # get list position of letter in menu
            _lvl2 = alpha_list_keys[complexname[2]][complexname]  # get position of complex type in letter in menu

            context_type = {"caption": "{0}".format(complexname), "children": []}
            context_root['children'][_lvl]['children'].append(context_type)

        # Second Interation: add complex types and fields
        for complexname in wsdl_json:
            _lvl = alpha_set_keys[complexname[2]]  # get list position of letter in menu
            # context_root['children'][_lvl]['children'].append(context_type)

            _lvl2 = alpha_list_keys[complexname[2]][complexname]  # get position of complex type in letter in menu

            for field in wsdl_json[complexname]:
                context_field = {"caption": "{0}".format(field), "command": "nsoa_insert_field", "args": {"field": "{0}".format(field)}}
                context_root['children'][_lvl]['children'][_lvl2]['children'].append(context_field)

        for num, letter in enumerate(context_root['children']):
            self.sort_list(
                context_root['children'][num]
            )

        with open(context_path, 'w') as f:
            json.dump(sublime_context_json, f)

        # INFO: This is a workaround to reload the plugin after the context menu is changed.
        sublime.save_settings('NSOA.sublime-settings')
        sublime.status_message('NSOA: Context menu updated.')

    def create_completions_list(self):
        """
        Create a list of completions using WSDL settings.

        """
        sublime_completions_json = {"scope": "source.js.nsoa"}

        settings = sublime.load_settings('NSOA.sublime-settings')
        wsdl_json = json.loads(settings.get('wsdl_json'))
        completions = []
        fields = set()

        for complexname in wsdl_json:
            completion = {}
            completion['trigger'] = complexname + "\tcomplex type "
            completion['contents'] = "NSOA.record.{0}".format(complexname) + "(${1:@id})"
            completions.append(completion)

            for field in wsdl_json[complexname]:
                fields.add(field)

        fields_sorted = self.sort_list(fields)

        for f in fields_sorted:
            suffix = "\tcustom field " if f[-3:] == '__c' else "\tfield "
            fcompletion = {}
            fcompletion['trigger'] = f + suffix
            fcompletion['contents'] = f
            completions.append(fcompletion)

        sublime_completions_json['completions'] = completions

        completions_path_list = ['User', 'NSOA', 'Wsdl.sublime-completions']
        completions_path = os.path.join(sublime.packages_path(), os.path.join(*completions_path_list))

        if not os.path.exists(os.path.dirname(completions_path)):
            os.makedirs(os.path.dirname(completions_path))

        with open(completions_path, 'w') as f:
            json.dump(sublime_completions_json, f)

        sublime.status_message('NSOA: Completions list updated.')

    def generate_wsdl(self, wsdl_url):
        status = self.validate_url(wsdl_url)

        if not status or status[0]['code'] == 1:
            sublime.error_message("The URL you provided is invalid.\nPlease review and try again.")
            return None
        else:
            url = status[0]['url']

        res = urllib.urlopen(url)
        tree = ET.parse(res)
        root = tree.getroot()

        library = {}
        for complextype in root.iter(XML_XS + 'complexType'):
            complexname = complextype.get('name')
            if complexname[:2] == 'oa':
                fields = []
                for element in complextype.iter(XML_XS + 'element'):
                    field = element.get('name')
                    type = element.get('type')
                    if type == 'xsd:string':
                        fields.append(field)
                fields_sorted = self.sort_list(fields)
                library[complexname] = fields_sorted

        json_data = json.dumps(library, sort_keys=True)

        settings = sublime.load_settings('NSOA.sublime-settings')
        if settings.has('wsdl_json'):
            settings.erase('wsdl_json')
        settings.set('wsdl_json', json_data)

        d = datetime.utcnow()
        dt = d.strftime('%A, %d %b %Y at %I:%M:%S %p (UTC)')
        settings.set('wsdl_last_updated', dt)

        self.create_context_menu()
        self.create_completions_list()

        sublime.save_settings('NSOA.sublime-settings')

        sublime.status_message('NSOA: WSDL data updated on {0}.'.format(dt))

    def remove_wsdl(self):
        """
        Removes all auto-completion entries, context menu entries,
        and WSDL settings entries.

        """
        # Remove WSDL objects and fields from completions...
        # TODO: Update this with logic to support checking for file
        completions_path_list = ['User', 'NSOA', 'Wsdl.sublime-completions']
        completions_path = os.path.join(sublime.packages_path(), os.path.join(*completions_path_list))

        if os.path.exists(completions_path):
            os.remove(completions_path)

        # Remove WSDL objects and fields context menu...
        context_path_list = ['User', 'NSOA', 'Context.sublime-menu']
        context_path = os.path.join(sublime.packages_path(), os.path.join(*context_path_list))

        if os.path.exists(context_path):
            os.remove(context_path)

        # Remove WSDL objects and fields from settings
        settings = sublime.load_settings('NSOA.sublime-settings')
        if settings.has('wsdl_json'):
            settings.erase('wsdl_json')

        if settings.has('wsdl_last_updated'):
            settings.erase('wsdl_last_updated')

        sublime.save_settings('NSOA.sublime-settings')
        sublime.status_message('NSOA: All WSDL data has been removed.')


class NsoaLoadGenericWsdl(NsoaGenerateWsdlBase):
    """
    A subclass for generating generic WSDL content.

    """
    def run(self):
        settings = sublime.load_settings('NSOA.sublime-settings')

        if settings.has('wsdl_last_updated'):
            last_updated = settings.get('wsdl_last_updated')
            dialog_msg = (
                'You last updated your WSDL data on {0}. '
                'Are you sure you want to overwrite your existing WSDL data?'.format(last_updated)
            )
            btn_text = 'Overwrite WSDL data'

            if sublime.ok_cancel_dialog(dialog_msg, btn_text):
                self.get_server_url()
        else:
            self.get_server_url()

    def get_server_url(self):
        settings = sublime.load_settings('NSOA.sublime-settings')

        server, port = '', ''
        if settings.has('server'):
            server = settings.get('server')
            # convert the colloquial production server to the correct domain prefix
            server = 'www' if server == 'production' else server

        if settings.has('port'):
            port = ':' + settings.get('port')

        if server == 'qa':
            server_url = 'http://{server}.openair1.com{port}/wsdl.pl?wsdl'.format(server=server, port=port)
        elif server:
            server_url = 'http://{server}.openair.com{port}/wsdl.pl?wsdl'.format(server=server, port=port)
        else:
            server_url = DEFAULT_WSDL_URL

        self.generate_wsdl(server_url)


class NsoaLoadAccountWsdl(NsoaGenerateWsdlBase):
    """
    A subclass for generating account-specific WSDL content.

    """
    def run(self):
        settings = sublime.load_settings('NSOA.sublime-settings')

        if settings.has('wsdl_last_updated'):
            last_updated = settings.get('wsdl_last_updated')
            dialog_msg = (
                'You last updated your WSDL data on {0}. '
                'Are you sure you want to overwrite your existing WSDL data?'.format(last_updated)
            )
            btn_text = 'Overwrite WSDL data'

            if sublime.ok_cancel_dialog(dialog_msg, btn_text):
                self.ask_for_url()
        else:
            self.ask_for_url()

    def ask_for_url(self):
        self.window.show_input_panel(
            'NSOA: Paste account-specific WSDL URL',
            '',
            self.generate_wsdl,
            None,
            None
        )


class NsoaRemoveWsdlData(NsoaGenerateWsdlBase):
    """
    A subclass for generating generic WSDL content.

    """
    def run(self):
        dialog_msg = (
            'MEASURE TWICE - CUT ONCE!\n\n'
            'You are about to remove all stored WSDL data, '
            'including auto-completions and context menu items.'
        )
        btn_text = 'Remove all WSDL data'
        if sublime.ok_cancel_dialog(dialog_msg, btn_text):
            self.remove_wsdl()


class NsoaOpenDocumentationBase(sublime_plugin.WindowCommand):
    """
    A base class for opening PDF documentation

    """
    def open_url_in_browser(self, url):
        """
        Opens the given url in a the default web browser.

        """
        sublime.status_message('NSOA: Opening {0}...'.format(url))
        webbrowser.open(url)


class NsoaOpenSoapGuide(NsoaOpenDocumentationBase):
    """
    Open the SOAP guide in a web browser.

    """
    def run(self):
        self.open_url_in_browser(SOAP_GUIDE_URL)


class NsoaOpenScriptingGuide(NsoaOpenDocumentationBase):
    """
    Open the User Scripting guide in a web browser.

    """
    def run(self):
        self.open_url_in_browser(SCRIPTING_GUIDE_URL)


class NsoaOpenScriptingReference(NsoaOpenDocumentationBase):
    """
    Open the User Scripting reference card in a web browser.

    """
    def run(self):
        self.open_url_in_browser(SCRIPTING_REFERENCE_URL)


class NsoaInsertField(sublime_plugin.TextCommand):
    """
    Inserts a WSDL field at the cursor(s).

    """
    def run(self, edit, **args):
        try:
            if args['field']:
                text = args['field']
            else:
                text = ''

        except Exception as e:
            sublime.error_message('NSOA: {0}: {1}'.format(type(e).__name__, e))
            return

        # Don't bother replacing selections if no text exists
        if text == '' or text.isspace():
            return

        # Do replacements
        for r in self.view.sel():
            # Insert when sel is empty to not select the contents
            if r.empty():
                self.view.insert(edit, r.a, text)
            else:
                self.view.replace(edit, r, text)
