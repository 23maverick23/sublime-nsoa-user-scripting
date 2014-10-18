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


## ----------------------------- GLOBAL CONSTANTS ---------------------------------------------------- ##
ST3 = sublime.version() >= '3000'

DEFAULT_WSDL_URL = 'http://www.openair.com/wsdl.pl?wsdl'
XML_XS = '{http://www.w3.org/2001/XMLSchema}'

SOAP_GUIDE_URL = 'http://www.openair.com/download/NetSuiteOpenAirSOAPAPIGuide.pdf'
SCRIPTING_GUIDE_URL = 'http://www.openair.com/download/NetSuiteOpenAirUserScriptingGuide.pdf'
SCRIPTING_REFERENCE_URL = 'http://www.openair.com/download/NetSuiteOpenAirUserScriptingReferenceCard.pdf'
## --------------------------------------------------------------------------------------------------- ##


class NsoaGenerateWsdlBase(sublime_plugin.WindowCommand):
    """
    A Sublime window command base class for loading WSDL files.

    """
    def get_package_file_path(self, path_list):
        """
        Gets the path to the file or folder specified. Expects
        a list of path directories.

        ex// ['NSOA', 'completions', 'wsdl.sublime-completions']

        """
        try:
            file_path = os.path.join(*path_list)
            packages_path = os.path.join(sublime.packages_path(), file_path)

            if sublime.platform() == 'windows':
                packages_path = packages_path.replace('\\', '/')

            if os.path.exists(packages_path):
                return packages_path
            else:
                sublime.error_message("Unable to find the necessary file at '{0}'.".format(packages_path))
                return None
        except Exception as e:
            print(e)

    def validate_url(self, url):
        """
        Validates the url against knows URL configurations
        Regex example: http://regex101.com/r/oK1eY1/1

        """
        status = []
        try:
            p = re.compile('^(?P<protocol>http(?:s)?)://(?P<subdomain>www|sandbox|demo|qa)\.openair(?:1)?\.com(?:\:)?(?P<port>\d+)?(?:|\/)/(?:wsdl\.pl\?)?(?P<wsdl>wsdl|\w+)?$', re.MULTILINE)
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
        context_path_list = ['NSOA', 'Context.sublime-menu']
        context_path = self.get_package_file_path(context_path_list)

        with open(context_path, 'r') as f:
            sublime_context = json.loads(f.read())

        wsdl_json = json.loads(settings.get('wsdl_json'))
        context_root = sublime_context[1]['children'][3]
        count = 0

        for complexname in wsdl_json:
            context_type = {"caption": "{0}".format(complexname), "children": []}
            context_root['children'].append(context_type)

            for field in wsdl_json[complexname]:
                context_field = {"caption": "{0}".format(field), "command": "nsoa_insert_field", "args": {"field": "{0}".format(field)}}
                context_root['children'][count]['children'].append(context_field)

            count += 1

        context_root['children'] = self.sort_list_dict(
            context_root['children'],
            'caption'
        )

        with open(context_path, 'w') as f:
            json.dump(sublime_context, f)

        sublime.status_message('NSOA: Context menu updated.')

    def create_completions_list(self):
        """
        Create a list of completions using WSDL settings.

        """
        sublime_completions = {"scope": "source.js.nsoa"}

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

        sublime_completions['completions'] = completions

        completions_path_list = ['NSOA', 'completions', 'Wsdl.sublime-completions']
        completions_path = self.get_package_file_path(completions_path_list)

        with open(completions_path, 'w') as f:
            json.dump(sublime_completions, f)

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
        settings.set('wsdl_json', json_data)
        sublime.save_settings('NSOA.sublime-settings')

        sublime.status_message('NSOA: Sublime settings updated.')
        self.create_context_menu()
        self.create_completions_list()

    def remove_wsdl(self):
        """
        Removes all auto-completion entries, context menu entries,
        and WSDL settings entries.

        """
        # Remove WSDL objects and fields from completions...
        completions_path_list = ['NSOA', 'completions', 'Wsdl.sublime-completions']
        completions_path = self.get_package_file_path(completions_path_list)

        with open(completions_path, 'w') as f:
            json.dump({}, f)

        # Remove WSDL objects and fields context menu...
        context_path_list = ['NSOA', 'Context.sublime-menu']
        context_path = self.get_package_file_path(context_path_list)

        with open(context_path, 'r') as f:
            sublime_context = json.loads(f.read())

        context_root = sublime_context[1]['children'][3]
        del context_root['children'][:]

        with open(context_path, 'w') as f:
            json.dump(sublime_context, f)

        # Remove WSDL objects and fields from settings
        settings = sublime.load_settings('NSOA.sublime-settings')
        if settings.has('wsdl_json'):
            settings.erase('wsdl_json')
            sublime.save_settings('NSOA.sublime-settings')

        sublime.status_message('NSOA: All WSDL data has been removed.')


class NsoaLoadGenericWsdl(NsoaGenerateWsdlBase):
    """
    A subclass for generating generic WSDL content.

    """
    def run(self):
        self.generate_wsdl(DEFAULT_WSDL_URL)


class NsoaLoadAccountWsdl(NsoaGenerateWsdlBase):
    """
    A subclass for generating account-specific WSDL content.

    """
    def run(self):
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
        msg = (
            'MEASURE TWICE - CUT ONCE!\n\n'
            'You are about to remove all NetSuite OpenAir WSDL data, '
            'including auto-completions and context menu items.'
        )
        if sublime.ok_cancel_dialog(msg, 'Remove all WSDL data'):
            self.remove_wsdl()


class NsoaOpenDocumentationBase(sublime_plugin.WindowCommand):
    """
    A base class for opening PDF documentation

    """
    def open_url_in_browser(self, url):
        """
        Opens the given url in a the default web browser.

        """
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
                text = ""

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
