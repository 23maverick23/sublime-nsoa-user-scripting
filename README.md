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

### After Installing...

After installing this package, make sure you configure your User settings file. The most important piece of this is to set your `server` and `port` settings, which are used to create the generic WSDL URL. If unset, the package will fall back on the production server WSDL URL _(Note: if you develop on QA or sandbox, this may mean that your WSDL data will not contain the most recent API objects and fields)_.

```json
{
    // This should hold the server you are connecting to.
    // Valid options are: "production", "sandbox", "demo", "qa"
    "server": "",

    // This optionally holds the port used to connect to
    // the above server (e.g. 1443).
    "port": ""
}
```

What's Included
---------------

### Screenshots

#### Command Palatte
![nsoa_command_palette.png](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_command_palette.png "sublime-nsoa-user-scripting")

#### Quick Tour: Basics
![nsoa_quick_tour_1.gif](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_quick_tour_1.gif "sublime-nsoa-user-scripting")

#### Quick Tour: Context Menu
![nsoa_quick_tour_2.gif](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_quick_tour_2.gif "sublime-nsoa-user-scripting")

#### Quick Tour: Account-Specific WSDL
![nsoa_quick_tour_3.gif](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/screenshots/nsoa_quick_tour_3.gif "sublime-nsoa-user-scripting")

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

- _NSOA.context_
    + remainingTime
    + remainingUnits
    + isTestMode
- _NSOA.form_
    + error
    + getAllValues
    + getLabel
    + getValue
    + getOldRecord
    + getNewRecord
- _NSOA.meta_
    + alert
    + log
    + log-debug
    + log-error
    + log-fatal
    + log-info
    + log-trace
    + log-warning
- _NSOA.wsapi_
    + add
    + delete
    + disableFilterSet
    + modify
    + read
    + upsert
    + whoami
    + enableLog
    + remainingTime

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

[LICENSE](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/LICENSE)

Changelog
---------

[CHANGELOG](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/raw/master/CHANGELOG)

Issues
------

You can log issues from the menu on the left, or by [clicking here](https://bitbucket.org/rmorrissey23/sublime-nsoa-user-scripting/issues/new).