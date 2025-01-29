
# Freegame rules
Every tumle increments the gloabl multiplier by +1
The global multiplier is applied to the tumble win
After all tumbles have completed: multiply tumble win by multipliers on board 
(multipliers on board do not increment the gloabl mult)
If there is a multiplier symbol on the board, this is added to the gloabl multiplier before the final evaluation

# Event descritpion
"winInfo" Summarises winning combinations. Includes multipliers, symbol postiions, payInfo [passed for every tumble event]
"tumbleBanner" includes values from the cumulative tumble, with global mult applied
"setWin" this the result for the entire spin (from on Reveal to the next). Applied after board has stopped tumbling
"seTotalWin" the cumulative win for a round. In the base-game this will be equal to the setWin, but in the bonus it will incrementally increase

