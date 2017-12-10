record ponto{
    int x,y;
}

int quadrado(int x){
    return x * x;
}

int iteracao(){
    int x = 0;
    while(x < 5){
        x++;
        if(x == 2) x = 5;
    }
    return x;
}
