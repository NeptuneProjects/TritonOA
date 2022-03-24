%aw.m
% Acoustic mode generation program using chebyshev polynomials
% as basis functions.

%set up depth of the ocean, note that the top must be at zero.
z=0:5:4000;
H=max(z)-min(z);

%set up sound speed profile, this particular one
% is the Munk profile but any will work.
B=1200; z0=1200.0;
c0=1492.0;
ep=0.006;
eta=2*(z-z0)/B;
c=c0*(1+ep*(eta+exp(-eta) -1));
clear B z0 c0 ep eta

% setup some key parameters
%fc is the acoustic frequency
fc=75;

%nm is the number of modes to solve for
nm=20;

%ncby is the number of chebyshev polynomials used
%to expand the modal solutions, (3*nm seems to be
%a good rule of thumb but more may be necessary)
ncby=floor(3*nm);

%cut is the number of chebyshev polynomials necessary 
%to model the sound speed profile (40 is a good number,
%but the number should always be less than ncby)
cut=40;

%daxis is the depth of the hydrophones where one 
%wants the solution of the mode shapes
daxis=25:25:3000;

%interpolate the sound slowness squared onto a 
%chebyshev grid
m=1./c; m=m.*m;
x=1-2*z/H;
N=ncby;
k=0:N-1;
xi=cos( k*pi/(N-1));
zi=H*(1-xi)/2;
mi=interp1(x,m,xi,'spline').';

%plot the result
%plot( log10(abs(mi)), 'r')
%pause

%do the chebyshev transform on the sound slowness
%squared and plot the resulting spectrum. Look
%at the plot and decide if cut is large enough
%to include most of the important terms.
mit=mi;
mit(1)=mit(1)/2; mit(N)=mit(N)/2;
Ker(1,:)=ones(size(xi));
Ker(2,:)=xi;
for ik=3:N
  Ker(ik,:)=2.*xi.*Ker(ik-1,:) - Ker(ik-2,:);
end
M=2*Ker*mit/(N-1);
M(1)=M(1)/2; M(N)=M(N)/2;
clear Ker ik mit
plot( log10(abs(M)), 'r')
semilogy( abs(M), 'r')
xlabel('Chebyshev number')
ylabel('Chebyshev coefficient')

fprintf("<return> to continue\n");
pause
M(cut:N)=zeros(N-cut+1,1);

%set up the chebshev differential operator
D=zeros(N,N);
for ik=2:N
  D(ik-1:-2:1,ik)=D(ik-1:-2:1,ik)+2*(ik-1)*ones(floor(ik/2),1);
end
D(1,:)=D(1,:)/2;
clear ik
%surf(D);
%pause

%the second derivative operator
D2=D*D;
%surf(D2);
%pause

%The convolution operator
G=zeros(N,N);
for ik=1:N 
  G(ik,1:ik)=G(ik,1:ik)+M(ik:-1:1).';
  G(ik,ik:N)=G(ik,ik:N)+M(1:N+1-ik).';
end
for ik=2:N 
  G(ik,1:N+1-ik)=G(ik,1:N+1-ik)+M(ik:N).';
end
G=G/2;
%surf(log10(abs(G)))
%pause

%the vertical wave equation operator
sc=2*pi*fc; 
L=4*D2/H/H + sc*sc*G;
%surf(log10(abs(L)))
%pause

%add in the boundary conditions, pressure release
%surface and bottom
bc(2,:)=ones(1,N);
bc(1,:)=(-1).^([0:N-1]);
cx=bc(:,N-1:N);
bc1=cx\bc;
LR=L(1:N-2,1:N-2) - L(1:N-2,N-1:N)*bc1(:,1:N-2);
%surf(log10(abs(LR)))
%pause

%solve the equation
[ V, k2]=eig(LR);

%extract the eigenvalues and plot them
k2=diag(k2);
ind=find( imag(k2)==0);
k2=k2(ind); V=V(:,ind);
ind=find( k2>0);
k2=k2(ind); V=V(:,ind);
[ k2, ind]=sort(k2);
V=V(:,ind);
k2=flipud(k2); V=fliplr(V);
nms=length(k2);
kh=sqrt(k2);
plot( kh(1:nm));
xlabel('Mode number')
ylabel('Horizontal wavenumber (radians/meter)')
%set( gca, 'ylim', [min(kh) max(kh)]);
fprintf("<return> to continue\n");
pause

%compute the mode phase speeds
cp=2*pi*fc./kh;
plot( cp(1:nm));
xlabel('Mode number')
ylabel('Phase speed (m/s)')
fprintf("<return> to continue\n");
pause

%set up the convolution and integral operators
% to calculate group speed by rayleigh's method
% and mode shape

%inverse chebyshev operator at mode depths
zr=daxis;
xr=1-2*zr/H;
clear Ker
Ker(1,:)=ones(size(xr));
Ker(2,:)=xr;
for ik=3:N-2
  Ker(ik,:)=2.*xr.*Ker(ik-1,:) - Ker(ik-2,:);
end

%integral operator
I=[0:N-2-1];
I=(I.*I - 1);
ind=find(I);
I(ind)=-2./I(ind);
I(2:2:N-2)=zeros(floor((N-2)/2),1);
clear ind

%convolution operator with slowness squared
G=zeros(N-2,N-2);
for ik=1:N-2
  G(ik,1:ik)=G(ik,1:ik)+M(ik:-1:1).';
  G(ik,ik:N-2)=G(ik,ik:N-2)+M(1:N-2+1-ik).';
end
for ik=2:N-2
  G(ik,1:N-2+1-ik)=G(ik,1:N-2+1-ik)+M(ik:N-2).';
end
G=G/2;

%loop on the number of valid modes
for ip=1:nms

  %convolution operator with mode shape squared
  V2=zeros(N-2,N-2);
  for ik=1:N-2
    V2(ik,1:ik)=V2(ik,1:ik)+V(ik:-1:1,ip).';
    V2(ik,ik:N-2)=V2(ik,ik:N-2)+V(1:N-2+1-ik,ip).';
  end
  for ik=2:N-2
    V2(ik,1:N-2+1-ik)=V2(ik,1:N-2+1-ik)+V(ik:N-2,ip).';
  end
  V2=V2/2;
  V2=V2*V(:,ip);

  % group speed integral
  iv2=H*I*V2/2;
  cg(ip)=iv2/(cp(ip)*H*I*G*V2/2);

  % mode shape inverse transform
  v(:,ip) = Ker.'*V(:,ip)/sqrt(iv2);

  % make sure the polarity is the same for all modes
  ind=find( abs(v(:,ip))>0.1*max(abs(v(:,ip))));
  if v(ind(length(ind)),ip)<0.0
    v(:,ip)=-v(:,ip);
  end

end

%plot the group speeds
plot( cg(1:nm))
xlabel('Mode number')
ylabel('Group speed (m/s)')
fprintf("<return> to continue\n");
pause

%plot the first 4 mode shapes
toshow=1:4;
plot( v(:,toshow), -daxis);
xlabel('Mode amplitude')
ylabel('Depth (m)')
fprintf("<return> to continue\n");
pause

%plot the mode chebyshev spectrum (if the rolloff
%is not fast enough increase ncby
plot( log10(abs(V(:,toshow)*diag(k2(toshow)))))
semilogy( abs(V(:,toshow)*diag(k2(toshow))))
xlabel('Chebyshev number')
ylabel('Chebyshev coefficient')
%hold on
%plot( log10(abs(LR*V(:,toshow))), 'ro')
%hold off
fprintf("<return> to continue\n");
pause
















