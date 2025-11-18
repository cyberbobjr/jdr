the refactoring of combat / narrative system is not efficient. Too complex. Check for this alternative (based on pydanticgraph https://ai.pydantic.dev/graph/)

A global state (choose a variable name) which indicate if player is in Combat or is in Narrative mode.
when a request is sent with "/api/gamesession/play" a node check the global state status.
If the global state is combat, the request is sent to "combat node"
if the global state is narrative, the request is sent to "narrative node"
Combat node declare a CombatAgent, with structured_output and tools. The structured output give "combat status (end, continue, player die, npc die, player flee, etc) narrative combat sequence, current turn action, damage taken, etc.etc." (think, understant and expand the concept). the combat agent use tools for getting initiative, give damage to combatant, heal combatant (when a npc or player use a heal potion or heal spell), give object for combatant, remove object to combatant, give xp to combatant, etc. (think, understant and expand the concept). 

If the combat status is end (player win or flee or die). the combat agent return change the "global state" and return combat result to the narrative node wich return the status of the game to the player. 
If the combat continue, "global state" left unchanged and player can continue to type sentence for giving instruction to the combat agent.

For the narrative node is more simple : it's just a narrative agent with "narrative tools", but if the player or foe attack or start a combat, the narrative agent use a combat tools for changing the "global state" to "combat mode" (instead narrative mode) and then the previous workflow is apply.

Refactor the "REFACTO_COMBAT.md" with these new instructions, ask questions if necessary.