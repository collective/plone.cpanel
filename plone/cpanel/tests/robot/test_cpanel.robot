*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Run keywords  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Variables ***

*** Test cases ***

Scenario: Creating a new plone site
    Given a brand new zope install
     when user enters "Dylan Jay" for "Your full name"
      and user enters "blah@blah.com" for "Email address"
      and user enters "My new site" for "Title"
      and user enters "newsite" for "Sub domain"
#      and user enters "blog" for "site theme"
      and Click button  Create New Plone Site
     then user will see "your new site has been created"
      and user will see "newsite.localhost"
     when user clicks "newsite.localhost"

*** Keywords ***

A brand new zope install
   go to  ${ZOPE_URL}

User enters "${text}" for "${label}"
   with the label  ${label}  input text  ${text}

With the label
    [arguments]     ${title}   ${extra_keyword}   @{list}
    ${for}=  Get Element Attribute  xpath=//label[starts-with(translate(normalize-space(.)," &#9;&#10;&#13", "-"), translate(normalize-space("${title}")," &#9;&#10;&#13", "-"))]@for
  #   ${for}  Execute Javascript   return $('label').filter(function(){return $(this).text().replace(/\s+/g,' ').trim()=='${title}'}).attr('for')[0]

    Run Keyword     ${extra_keyword}  id=${for}   @{list}



second menu should be visible
    Element Should Be Visible  xpath=(//dl[contains(@class, 'actionMenu')])[2]

first menu should not be visible
    Wait until keyword succeeds  10s  1s  Element Should Not Be Visible  xpath=(//dl[contains(@class, 'actionMenu')])[1]//dd

I click outside of menu
    Click Element  xpath=//h1


I copy the page
    Open Action Menu
    Click Link  link=Copy
    Page should contain  copied

I paste
    Go to  ${PLONE_URL}
    Open Action Menu
    Click Link  link=Paste

I should see '${message}' in the page
    Wait until page contains  ${message}
    Page should contain  ${message}
