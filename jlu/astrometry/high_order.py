import numpy as np
from scipy.optimize import curve_fit, minimize
from scipy import interpolate
from numpy.polynomial.legendre import legfit, legval2d




class transform:
    
    def __init__(self, x1, y1, x_ref, y_ref, order_poly=3,order_spline=2 ,num_knots=2, smooth=False, smooth_fac=None, weights=None, fit_spline_b=True, leg=False, verbose=False ):
        '''
        
    
        args
        ----------------------------
        x1,y1 - 1d array of rereference coordinates
        xref, yref - 1d array of master coordiantes that correspond to x1 and y1

        keywords
        -------------------------------
        order  - int, order of polynomial used
        num_knots - int, number of knots used by spline fit
        smooth_fac - float, optional parameter that sets smoothing factor used in LSQBivariateSpline
        smooth -  bool, if True spline fit uses smooth version (interpolate.SmoothBivariateSpline) note that num_knots is then unused
        leg -- use legendere basis for polynomial fit -- recoomend to using spline when you do this

        weights - array of weights for the input data points, must be same length
        x_new, y_new - transformed coordinates, correspondds to reference frame
        spline_x, spline_y - spline transformation objects (see scipy.interpolate.BivariateSpline)
        coeff_x,coeff_y - polynomial coefficients for the polynomial fit
        '''
        
        order_dict = {0:1,1:3,2:6,3:10,4:15,5:21,6:28,7:36}
        num_poly_param = order_dict[order_poly]
    
        

        '''
        Fit polynomial to requested order
        '''


        self.fit_spline_b=fit_spline_b
        self.x1 = x1
        self.y1 = y1 
        self.y_ref = y_ref 
        self.x_ref = x_ref
        self.leg = leg
        self.order_poly = order_poly
        
        if weights != None:
            self.weights = weights
        else:
            weights = np.ones(x1.shape)
            self.weights = weights
            
        if not leg:

            
            cur_or = 1
            p0x = np.zeros(order_dict[cur_or])
            p0y = np.zeros(order_dict[cur_or])
            
            while cur_or < order_poly + 1:
                coeff_x, coeff_y = fit_poly(x1, y1, x_ref, y_ref, order_dict[cur_or], p0x=p0x, p0y = p0y, weights=weights)
                cur_or += 1
                p0x = np.zeros(order_dict[cur_or])
                p0y = np.zeros(order_dict[cur_or])

                for i in range(len(coeff_x)):
                    p0x[i] = coeff_x[i]
                    p0y[i] = coeff_y[i]

                    x_poly = poly(np.array([x1,y1]), coeff_x)
                    y_poly = poly(np.array([x1, y1]), coeff_y)
                
       
                    '''
                    Now do spline fit on residual
                    '''


        if self.fit_spline_b:
            dx , spline_x =  fit_spline(x_poly, y_poly, x_ref-x_poly, num_knots=num_knots, smooth=smooth, smooth_fac=smooth_fac, weights=weights, order=order_spline)
            dy , spline_y =  fit_spline(x_poly, y_poly, y_ref-y_poly, num_knots=num_knots, smooth=smooth, smooth_fac=smooth_fac, weights=weights, order=order_spline)
            x_new = dx + x_poly
            y_new = dy + y_poly
                

                
            self.spline_x = spline_x
            self.spline_y = spline_y
        self.coeff_x = coeff_x
        self.coeff_y = coeff_y
    

    else:
        #first renormalize x and y

        self.normalize0()
        if verbose:
            print 'fitting Legendre Polynomials to ',len(self.x_norm),'points with ',self.order_poly**2,' coefficients'
        self.fit_leg()
            
            

        #self.coeff_x = legfit(x1, y1, x_ref, order_poly, w=weights)
        #self.coeff_y = legfit(x1, y1, y_ref, order_poly, w=weights)

    
    def evaluate(self, x,y):
        if not self.leg:
            x_poly = poly(np.array([x,y]), self.coeff_x)
            y_poly = poly(np.array([x,y]), self.coeff_y)

            if not self.fit_spline_b:
                return x_poly, y_poly
       
            x_poly = self.spline_x.ev(x_poly, y_poly) + x_poly
            y_poly = self.spline_y.ev(x_poly, y_poly) + y_poly
        else:
            x_in = self.norm(x,axis='x')
            y_in = self.norm(y,axis='y')
            
            x_poly = self.rnorm(legval2d(x_in, y_in, self.c_x), 'x')
            y_poly = self.rnorm(legval2d(x_in, y_in, self.c_y), 'y')

       
        return x_poly, y_poly

    def norm(self, x, axis):
        '''
        x is vector to be normalize, axis is either 'x' or 'y' to ensure use of correct normalization
        '''

        if axis == 'x':
            return (x - self.x10) / (self.xdiv) - 1.0
        elif axis =='y':
            return (x - self.y10) / (self.ydiv) -1.0
        
    def rnorm(self,x,axis):
        '''
        reverses normalization process for use outside
        '''
        if axis=='x':
            return (x+1.0)   * self.xdiv + self.x10
        elif axis =='y':
            return (x+1.0)   * self.ydiv + self.y10 
        
            
        
    def normalize0(self):
       
        if np.min(self.x1) < 0:
            self.x10 = np.min(self.x1)
            self.x_norm = self.x1 - self.x10
            self.x_ref_norm = self.x_ref - self.x10 
                
        else:
            self.x10 = 0
            self.x_norm = self.x1
            self.x_ref_norm = self.x_ref
                
        if np.min(self.y1) < 0:
            self.y10 = np.min(self.y1)
            self.y_norm = self.y1 - self.y10
            self.y_ref_norm = self.y_ref - self.y10

        else:
            self.y10 = 0
            self.y_norm = self.y1
            self.y_ref_norm = self.y_ref
            
        self.xdiv =  1100 #np.max(self.x_norm)
        self.ydiv =  1100 #np.max(self.y_norm)

        self.x_norm = self.x_norm / self.xdiv - 1.0
        self.x_ref_norm = self.x_ref_norm / self.xdiv - 1.0 
        
        self.y_norm = self.y_norm / self.ydiv - 1.0 
        self.y_ref_norm = self.y_ref_norm / self.ydiv - 1.0
            
    def fit_leg(self):
        p0x = np.ones(self.order_poly**2)
        p0y = np.ones(self.order_poly**2)
        c_x , cov_x = curve_fit(self.leg_func, np.array([self.x_norm,self.y_norm]), self.x_ref_norm, p0=p0x, sigma=1.0/self.weights)
        c_y , cov_y = curve_fit(self.leg_func, np.array([self.x_norm,self.y_norm]), self.y_ref_norm, p0=p0y, sigma=1.0/self.weights)

        self.c_x = np.reshape(c_x, (self.order_poly, self.order_poly))
        self.c_y = np.reshape(c_y, (self.order_poly, self.order_poly))
            
            
    def leg_func(self, xdata, *c):     

        #print c
        c_a = np.reshape(c,(self.order_poly,self.order_poly))
        return legval2d(xdata[0,:], xdata[1,:] ,c_a)

def fit_poly(x1, y1, xref, yref, num_free_param , p0x = None, p0y=None, minim=False, weights=None):
    '''
    Assumes input is 2 matched starlists (x1, y1, x2, y2)
    free_param is number of free parameters to be used in the fit
    returns coefficients for best fit polynomial in both x and y
    '''

    if p0x ==None:
        p0x = np.ones(num_free_param)
    if p0y == None:
        p0y = np.ones(num_free_param)


    if not minim:
        c_x, cov_x = curve_fit(poly, np.array([x1,y1]), xref, p0=p0x, sigma=1.0/weights)
        c_y, cov_y = curve_fit(poly, np.array([x1,y1]), yref, p0=p0y, sigma=1.0/1weights)
    else:
        for i in range(len(p0x)):
            p0x[i] = p0x[i]# + i * .01
            p0y[i] = p0y[i]# + i * .01
        resx = minimize(poly_min,p0x, args=(np.array([x1,y1]), xref))
        resy = minimize(poly_min,p0y, args=(np.array([x1,y1]), yref))
        c_x = resx.x
        c_y = resy.x
    return c_x, c_y  
    
def poly_min(param_vec, data, ref ):
    '''
    Performs Polynomial Transformation up to number of coefficients it is given
    '''


    if len(param_vec) == 1:
        param_vec = param_vec[0]

        
    x = data[0,:]
    y = data[1,:]

    exp1 = 1
    exp2 = 0
    level= 1
    x_new = np.zeros(len(x)) + param_vec[0]
    i = 1
    cont = True 
    while i < len(param_vec):
        x_new = x_new + param_vec[i] * x**exp1 * y**exp2 
        i +=1 
            

        if exp2 == level:
            level += 1
            exp1 = level
            exp2 = 0 
        else:
            exp1 = exp1 - 1 
            exp2 = exp2 + 1
            
    return np.sum(np.abs(x_new - ref))

def poly(data, *param_vec):
    '''
    Performs Polynomial Transformation up to number of coefficients it is given
    '''


    if len(param_vec) == 1:
        param_vec = param_vec[0]

        
    x = data[0,:]
    y = data[1,:]

    exp1 = 1
    exp2 = 0
    level= 1
    x_new = np.zeros(len(x)) + param_vec[0]
    i = 1
    cont = True 
    while i < len(param_vec):
        x_new = x_new + param_vec[i] * x**exp1 * y**exp2 
        i +=1 
            

        #print exp1, exp2
        if exp2 == level:
            level += 1
            exp1 = level
            exp2 = 0 
        else:
            exp1 = exp1 - 1 
            exp2 = exp2 + 1
            
    return x_new 

def fit_spline( x, y, x_ref, knot_x=None, knot_y=None, num_knots=5, smooth=False, smooth_fac=None, weights=None, order=3):
        '''
        performs spline fit of the form dx = f(x,y)
        knot_x/knot_y are 1-d arrays that are the  x and y coordinates of knot locations
        '''
        if knot_x == None:
            knot_x = np.linspace(np.min(x), np.max(x), num=num_knots)
        if knot_y == None:
            knot_y = np.linspace(np.min(y), np.max(y), num=num_knots)
    

        if not smooth:
            if smooth_fac == None:
                spline = interpolate.LSQBivariateSpline(x, y, x_ref, knot_x, knot_y, kx=order, ky=order, w=weights)
                x_new = spline.ev(x, y)
            else:
                spline = interpolate.LSQBivariateSpline(x, y, x_ref, knot_x, knot_y, kx=order, ky=order,w=weights, s=smooth_fac)
                x_new = spline.ev(x, y)
        else:
            spline = interpolate.SmoothBivariateSpline(x, y, x_ref, w=weights)
            x_new = spline.ev(x, y)
        return x_new, spline 
