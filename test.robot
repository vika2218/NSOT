*** Settings ***
Library     test.py


*** Test Cases ***
Testing Hostname Configuration
    log to console      ${\n}
	log to console      Hostname configuration and verifiication started
	${result} =         host
	log to console      ${result}
    log to console      Hostname function verification done! Results are as shown above

Testing Reachability
    log to console      ${\n}
    log to console      Reachability test started
    ${op2}              reachability_test
    should be equal     ${op2}              0
    log to console      Reachability test completed

Verifying Flow Entries (SDN)
    log to console      ${\n}
    log to console      Flow entries configuration and verifiication started
    flow_test
    log to console      Flow entries configuration and verifiication completed

