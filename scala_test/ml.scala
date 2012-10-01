import scalala.scalar._;
import scalala.tensor.dense._;
import scala.io._;
import scalala.library.LinearAlgebra._;
import scala.math._
import scala.util._

import java.io._;

object Hi {
      var data : List[Array[Double]] = Nil
      var beta = DenseVector.zeros[Double](3)

      def main(args: Array[String]) = {
        println("Reading data...")
        Source.fromFile("out/test.csv").getLines().foreach{ l =>
          val bits : Array[String] = l.split(",")
          data ::= Array(bits(0).toDouble, bits(1).toDouble, bits(2).toDouble)
        }
        //ols()

       //gradient_descent()
        stochastic_gd()
        //gridsearch()
      } 
     
      // Ordinary Least Squares
      def ols() = {
        var x = DenseMatrix.zeros[Double](data.length, 3)
        var y = DenseVector.zeros[Double](data.length)
        for ( (row,i) <- data.zipWithIndex){
          x(i,0) = 1
          x(i,1) = row(0)
          x(i,2) = row(1)
          y(i) = row(2)
        }
        println("Inverting matrix...")
        var z = pinv(x) * y
        var p = x*pinv(x)
        var m = DenseMatrix.eye[Double](data.length) - p
        val s2 : Double = y.t*m*y/(data.length - 3)
        val s = sqrt(s2)
        println("s = " + s)
        val cov = inv(x.t*x) * s2 
        println("Parameter Covariance Matrix")
        println(cov)
        println("Result")
        for(i <- 0 to 2){
          println("beta" + i+ " = " + z(i) + " +- " + sqrt(cov(i,i)))
        }
      }

      // Gradient Descent
      def gradient_descent() = {
        val bold = true
        var alpha : Double = 0.001 //0.01
        val N = data.length
        beta = DenseVector(1, -40, 40)
        var cost : Double = 0
        var cost_m1 : Double = -1 
        
        val wrt = new PrintWriter(new File("out/gradient_descent_bold.out"))
        for(i <- 1 to 20000){
          var dbeta = DenseVector.zeros[Double](3)
          cost = 0
          for(d <- data){
              val y = d(2)
              val x = DenseVector(1, d(0), d(1))
              val err = beta.t*x - y
              for(j <- 0 to 2){
                dbeta(j) -= alpha * (1.0/N) * err * x(j)
              }
              cost += err*err
          }
          wrt.println(i + "\t"+ alpha + "\t" + cost + "\t" + beta(0) + "\t" + beta(1) + "\t" + beta(2))
          if(i % 10000 == 0) println(i + " " + beta)
          beta += dbeta
          alpha = if (!bold) alpha
                  else if(cost < cost_m1) alpha*1.05
                  else alpha*0.5
          cost_m1 = cost
 
       }
       wrt.close()
      }

      // Perform Stochastic Gradient Descent
      def stochastic_gd() = {
        val bold = true
        var alpha : Double = 0.0001
        var dbeta = DenseVector.zeros[Double](3) 
        beta = DenseVector(1, -40, 40)
        var cost : Double = 0
        val wrt = new PrintWriter(new File("out/stochastic_gradient_descent.out"))

        val N = data.length
        var sdata = Array.ofDim[Double](N, 3)

        for ((d, i) <- data.zipWithIndex){
          sdata(i) = d
        }

        var rnd = Random

        for(i <- 0 to 100000){
          if( i % N == 0){
            cost = 0
            for(d <- data){
              val err = beta.t*DenseVector(1, d(0), d(1)) - d(2)
              cost += err*err
            }
           wrt.println((i+N)/N + "\t" + cost + "\t" + beta(0) +"\t" + beta(1) + "\t" + beta(2))
          }
          
          val rndi = rnd.nextInt(N)
          val d = sdata(rndi)
          dbeta = DenseVector.zeros[Double](3)
          val y = d(2)
          val x = DenseVector(1, d(0), d(1))
          val err = beta.t*x - y
          for(j <- 0 to 2){
            dbeta(j) -= alpha * err * x(j)
          }
          beta = beta + dbeta
        }
        wrt.close()
      }

      // Evaluate objective function using grid search
       def gridsearch() = {
         val nstep = 500
         val minv = -100
         val maxv = 100
          val wrt = new PrintWriter(new File("out/gridsearch.out"))
          //for(b1 <- 0 to nstep){
          val b1 = 5
            println(b1)
            for(b2 <- 0 to nstep){
              for(b3 <- 0 to nstep){
                beta = DenseVector(minv + (maxv-minv)*b1/nstep,
                                   minv + (maxv-minv)*b2/nstep,
                                   minv + (maxv-minv)*b3/nstep)
                var cost : Double = 0
                for(d <- data){
                  val y = d(2)
                  val x = DenseVector(1, d(0), d(1))
                  val err = beta.t*x - y
                  cost += err*err
                }
                wrt.println(beta(0)+"\t" + beta(1) + "\t" + beta(2) + "\t" + cost)
              }
            }
            
          //}
          wrt.close
      }
}


