while(totalAshes > ashesPerBowl){
    emptyBowl();
    packNewBowl();

    while( !bowlIsOver && waterIsCold ){
        while( ashesAreBurning ){
            if( urgeToCough == 0 ){
                smoke();
            }
        }
        stir();
    }
    
    emptyWater();
    goInside();
}
