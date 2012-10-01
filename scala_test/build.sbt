libraryDependencies  ++= Seq(
            // other dependencies here
                        "org.scalala" %% "scalala" % "1.0.0.RC2"
                        )

resolvers ++= Seq(
            // other resolvers here
                        "Scala Tools Snapshots" at "https://oss.sonatype.org/content/groups/scala-tools/",
                                    "ScalaNLP Maven2" at "http://repo.scalanlp.org/repo"
                                    )

scalaVersion := "2.9.1"
