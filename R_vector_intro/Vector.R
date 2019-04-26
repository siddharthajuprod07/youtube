--Vectors
x <- c(10.4,2.3,50.7,3.5)
C(7) # Not going to work as R is case sensitive 
y = c(10.4,2.3,50.7,3.5)
assign("z",c(10.4,2.3,50.7,3.5))
c(10.4,2.3,50.7,3.5) -> m
1/x
k = c(x,y,z)

--Sequences
-3 : 3 #Forward sequence
c(-3,-2,-1,0,1,2,3)
2*-3:3
n=10
1:n-1
1:(n-1)
3:-3 #Backward Sequence
?seq
seq(-6,6)
seq(-6,6,2)
seq(from=-6,by=2,length.out = 7)
seq(from=-6,by=2,along.with = y)
seq(by=2,along.with = y,from=-6)
seq(from=-6,by=2,length.out = 7,along.with = y)
seq(along.with = y)
seq()
rep(y,times=5)
rep(y,each=5)
rep(y,each=5,length.out=3)