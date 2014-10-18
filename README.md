sublime-nsoa-user-scripting
===================

A Sublime Text package containing helpful tools for NetSuite OpenAir User Scripting.

### New in this Release

Version 2.0 of the NSOA User Scripting package includes some major enhancements, including the ability to generate auto-completions directly from your account specific WSDL URL, as well as a handy right-click context menu for viewing and pasting API object fields directly from your WSDL. Lastly, you can open PDF documentation guides quickly from the command palette, right-click context menu, or the _Tools > NSOA_ menu.

Installation
------------

### Package Control

You can install this package using [Package Control](https://sublime.wbond.net/packages/NSOA) from wbond.net.

- Press `ctrl+shift+p` (Windows/Linux) or `command+shift+p` (OS X) to bring up the Command Palette (or use _Tools > Command Palette_ menu)
- Type to search for the `Package Control: Install Package` command
- Search packages for **NSOA** and hit `enter` to install
- **NOTE:** You may need to restart in order to use this package

### Manual

[Clone](https://rmorrissey23@bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting.git) or [download](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/get/master.zip) the contents of this repo into your Sublime Text `Packages` folder.

- OS X: `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`
- Windows: `%APPDATA%\Sublime Text 3\Packages`
- Linux: `~/.config/sublime-text-3/Packages`

What's Included
---------------

### Screenshots

![nsoa_command_palette.png](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_command_palette.png "sublime-nsoa-user-scripting")

![nsoa_context_menu.png](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_context_menu.png "sublime-nsoa-user-scripting")

> Theme: [Centurion](https://sublime.wbond.net/packages/Theme%20-%20Centurion)
> Color Scheme: [Tomorrow Night](https://sublime.wbond.net/packages/Tomorrow%20Color%20Schemes)
> Font: [Source Code Pro](https://github.com/adobe/source-code-pro)

### Syntaxes

- JavaScript (NSOA)

### Commands

- NSOA: Load Generic WSDL
- NSOA: Load Account-Specific WSDL
- NSOA: Open Quick Reference Card
- NSOA: Open SOAP API Guide
- NSOA: Open User Scripting Guide
- NSOA: Remove All WSDL Data

### Completions (Default)

- remainingTime
- remainingUnits
- isTestMode
- error
- getAllValues
- getLabel
- getValue
- getOldRecord
- getNewRecord
- alert
- log
- log-debug
- log-error
- log-fatal
- log-info
- log-trace
- log-warning
- add
- delete
- disableFilterSet
- modify
- read
- upsert
- whoami
- enableLog
- remainingTime

### Snippets

```javascript
// attribute
{
    name: "${1:limit}",
    value: "${2:100}"
}

// function
function ${1:useCamelCase}(type) {
    try {
        $0
    } catch(e) {
        NSOA.meta.log('error', 'Try/catch error: ' + e);
    }
}

// header
/**
 * Copyright NetSuite, Inc. 2014 All rights reserved.
 * The following code is a demo prototype. Due to time constraints of a demo,
 * the code may contain bugs, may not accurately reflect user requirements
 * and may not be the best approach. Actual implementation should not reuse
 * this code without due verification.
 *
 * ${2:Short description of script file}
 *
 * Version    Date            Author           Remarks
 * 1.00       ${1:@date }     Ryan Morrissey
 *
 */


// read_error_check
function readErrorCheck(readResult) {
    if (!readResult || !readResult[0]) {
        NSOA.meta.log('error', 'No read objects returned.');
        return;
    } else if (readResult[0].errors !== null && readResult[0].errors.length > 0) {
        readResult[0].errors.forEach(function(err) {
            var fullError = err.code + ' - ' + err.comment + ' ' + err.text;
            NSOA.meta.log('error', 'Error: ' + fullError);
        });
        return;
    } else {
        return readResult;
    }
}

// read_request
{
    type       : "${1}",
    method     : "${2:equal to}",
    fields     : "${3}",
    attributes : [${4}],
    objects    : [${5}]
}

// update_error_check
function updateErrorCheck(updateResult) {
    if (!updateResult || !updateResult[0]) {
        NSOA.meta.log('error', 'No update objects returned.');
        return;
    } else if (updateResult[0].errors !== null && updateResult[0].errors.length > 0) {
        updateResult[0].errors.forEach(function(err) {
            var fullError = err.code + ' - ' + err.comment + ' ' + err.text;
            NSOA.meta.log('error', 'Error: ' + fullError);
        });
        return;
    } else {
        return updateResult;
    }
}

```

License
-------

[LICENSE](LICENSE)

Issues
------

You can log issues from the menu on the left, or by [clicking here](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/issues/new).

Contribute
----------

1. [Fork](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/fork) this repo.
2. Create a branch `git checkout -b my_feature`
3. Commit your changes `git commit -am "Added Feature"`
4. Push to the branch `git push origin my_feature`
5. Open a [Pull Request](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/pull-request/new)