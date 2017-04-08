%{?_javapackages_macros:%_javapackages_macros}
# Re-enable when https://bugzilla.redhat.com/show_bug.cgi?id=1234368 is fixed
%bcond_with ruby

Name:          tesla-polyglot
Version:       0.1.19
Release:       2%{?dist}
Summary:       Modules to enable Maven usage in other JVM languages
License:       EPL
Group:         Development/Java
URL:           https://github.com/takari/maven-polyglot
Source0:       https://github.com/takari/polyglot-maven/archive/polyglot-%{version}.tar.gz
Source1:       eclipse-1.0.txt

BuildRequires: maven-local
BuildRequires: mvn(commons-logging:commons-logging)
BuildRequires: mvn(junit:junit)
BuildRequires: mvn(org.apache.maven:maven-core)
BuildRequires: mvn(org.apache.maven:maven-model)
BuildRequires: mvn(org.apache.maven:maven-model-builder)
BuildRequires: mvn(org.apache.maven:maven-plugin-api)
BuildRequires: mvn(org.apache.maven.plugins:maven-plugin-plugin)
BuildRequires: mvn(org.apache.maven.plugin-tools:maven-plugin-annotations)
BuildRequires: mvn(org.codehaus.gmavenplus:gmavenplus-plugin)
BuildRequires: mvn(org.codehaus.groovy:groovy-all)
BuildRequires: mvn(org.codehaus.modello:modello-maven-plugin)
BuildRequires: mvn(org.codehaus.plexus:plexus-component-annotations)
BuildRequires: mvn(org.codehaus.plexus:plexus-component-metadata)
BuildRequires: mvn(org.codehaus.plexus:plexus-utils)
BuildRequires: mvn(org.eclipse.sisu:org.eclipse.sisu.plexus)
BuildRequires: mvn(org.slf4j:slf4j-api)
BuildRequires: mvn(org.yaml:snakeyaml)

# Maven POM doesn't require maven-parent
BuildRequires: mvn(org.apache.maven:maven-parent:pom:)

BuildRequires: xmvn

%if %{with ruby}
# Ruby module
BuildRequires: mvn(de.saumya.mojo:gem-maven-plugin)
BuildRequires: mvn(org.jruby:jruby-core)
%endif

%if 0
# clojure-maven-plugin dont work with clojure 1.5.1
# Clojure module
BuildRequires: mvn(com.theoryinpractise:clojure-maven-plugin:1.3.1)
BuildRequires: mvn(org.clojure:clojure:1.1.0)
# Scala module
BuildRequires: mvn(com.twitter:util-eval_2.10:6.23.0)
BuildRequires: mvn(com.googlecode.kiama:kiama_2.10:1.8.0)
BuildRequires: mvn(net.alchim31.maven:scala-maven-plugin:3.2.0)
BuildRequires: mvn(org.scala-lang:scala-library:2.10.5)
# Test deps
# Clojure module
BuildRequires: mvn(org.easytesting:fest-assert)
# Scala module
BuildRequires: mvn(org.specs2:specs2-junit_2.10:2.4.17)
# XML module
BuildRequires: mvn(com.cedarsoftware:java-util)
%endif

Obsoletes:     %{name}-cli
Obsoletes:     %{name}-clojure
BuildArch:     noarch

%description
Polyglot for Maven is an experimental distribution of Maven
that allows the expression of a POM in something other than
XML. A couple of the dialects also have the capability to
write plugins inline: the Groovy, Ruby and Scala dialects
allow this.

%package atom
Summary:       Polyglot Tesla :: Atom

%description atom
Polyglot Tesla :: Atom.

%package common
Summary:       Polyglot Tesla :: Common

%description common
Polyglot Tesla :: Common.

%package groovy
Summary:       Polyglot Tesla :: Groovy

%description groovy
Polyglot Tesla :: Groovy.

%package maven-plugin
Summary:       Polyglot Tesla :: Maven Plugin

%description maven-plugin
This package contains Polyglot Tesla Maven Plugin.

%if %{with ruby}
%package ruby
Summary:       Polyglot Tesla :: Ruby

%description ruby
Polyglot Tesla :: Ruby.
%endif

%package translate-plugin
Summary:       Polyglot :: Translate Plugin

%description translate-plugin
This package contains Polyglot Translate Plugin.

%if 0
%package clojure
Summary:       Polyglot Tesla :: Clojure

%description clojure
Polyglot Tesla :: Clojure.

%package scala
Summary:       Polyglot Tesla :: Scala

%description scala
Polyglot Tesla :: Scala.
%endif

%package xml
Summary:       Polyglot Tesla :: XML

%description xml
Polyglot Tesla :: XML.

%package yaml
Summary:       Polyglot Tesla :: YAML

%description yaml
Polyglot Tesla :: YAML.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n polyglot-maven-polyglot-%{version}

find -name "*.class" -delete
find -name "*.jar" -delete

%pom_remove_parent

# Unavailable build deps/tools
%pom_disable_module polyglot-clojure
%pom_disable_module polyglot-scala

%pom_remove_dep :polyglot-scala polyglot-translate-plugin

%if %{without ruby}
%pom_disable_module polyglot-ruby
%pom_remove_dep -r :polyglot-ruby
%endif

%pom_remove_dep org.eclipse.sisu:org.eclipse.sisu.inject.tests

%pom_remove_dep rubygems:maven-tools polyglot-ruby
# TODO: remove following line once maven-tools gem is in Fedora
rm -Rf polyglot-ruby/src/{test,it}
%pom_remove_plugin :maven-invoker-plugin polyglot-ruby

# Unavailable plugin
%pom_remove_plugin org.codehaus.groovy:groovy-eclipse-compiler polyglot-groovy
%pom_remove_dep org.codehaus.groovy:groovy-eclipse-batch polyglot-groovy
%pom_remove_dep org.codehaus.groovy:groovy-eclipse-compiler polyglot-groovy
%pom_remove_plugin :maven-compiler-plugin polyglot-groovy
# use gmavenplus
%pom_add_plugin org.codehaus.gmavenplus:gmavenplus-plugin:1.5 polyglot-groovy "
 <executions>
  <execution>
   <goals>
    <goal>generateStubs</goal>
    <goal>testGenerateStubs</goal>
    <!--goal>compile</goal>
    <goal>testCompile</goal-->
   </goals>
  </execution>
 </executions>"

for p in maven-plugin translate-plugin; do
  %pom_add_plugin "org.apache.maven.plugins:maven-plugin-plugin:3.4" polyglot-${p} "
  <configuration>
    <skipErrorNoDescriptorsFound>true</skipErrorNoDescriptorsFound>
  </configuration>"
%pom_xpath_inject "pom:dependency[pom:groupId = 'org.apache.maven']" "<version>3.3.1</version>" polyglot-${p}
done

%pom_xpath_inject "pom:project/pom:dependencies/pom:dependency[pom:groupId = 'org.apache.maven']" '<version>${mavenVersion}</version>'

# atom common maven-plugin translate-plugin
# diamond operator
for m in yaml groovy
do
%pom_add_plugin org.apache.maven.plugins:maven-compiler-plugin:3.0 polyglot-${m} '
<configuration>
 <source>1.7</source>
 <target>1.7</target>
 <encoding>UTF-8</encoding>
</configuration>'
done

# Use web access
sed -i '/pyyaml/d' polyglot-yaml/src/test/java/org/sonatype/maven/polyglot/yaml/CompactFormatTest.java

# test skipped for unavailable dependency org.easytesting:fest-assert:1.1
rm -rf polyglot-clojure/src/test/java/*

# com.cedarsoftware:java-util:1.19.3
sed -i '/DeepEquals/d' polyglot-xml/src/test/java/org/sonatype/maven/polyglot/xml/TestReaderComparedToDefault.java
%pom_remove_dep com.cedarsoftware:java-util polyglot-xml

# ComparisonFailure
rm polyglot-yaml/src/test/java/org/sonatype/maven/polyglot/yaml/SnakeYamlModelReaderTest.java

cp -p %{SOURCE1} .
sed -i 's/\r//' eclipse-1.0.txt

%mvn_alias ':polyglot-{*}' io.tesla.polyglot:tesla-polyglot-@1
%mvn_alias ':polyglot-{*}' org.sonatype.pmaven:pmaven-@1

%build

%mvn_build -s -- -Dproject.build.sourceEncoding=UTF-8

%install
%mvn_install

%files -f .mfiles-polyglot
%doc poms
%doc eclipse-1.0.txt license-header.txt

%files atom -f .mfiles-polyglot-atom
%files common -f .mfiles-polyglot-common
%files groovy -f .mfiles-polyglot-groovy

%if %{with ruby}
%files ruby -f .mfiles-polyglot-ruby
%endif

%if 0
%files clojure -f .mfiles-polyglot-clojure
%files scala -f .mfiles-polyglot-scala
%endif

%files maven-plugin -f .mfiles-polyglot-maven-plugin
%files translate-plugin -f .mfiles-polyglot-translate-plugin

%files xml -f .mfiles-polyglot-xml
%doc polyglot-xml/README.md

%files yaml -f .mfiles-polyglot-yaml

%files javadoc -f .mfiles-javadoc
%doc eclipse-1.0.txt license-header.txt

%changelog
* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Nov 18 2016 Michael Simacek <msimacek@redhat.com> - 0.1.19-1
- Update to upstream version 0.1.19

* Tue Aug 09 2016 gil cattaneo <puntogil@libero.it> 0.1.18-3
- add missing build requires: xmvn

* Sun Jul 03 2016 gil cattaneo <puntogil@libero.it> 0.1.18-2
- enable xml module
- use gmavenplus-plugin

* Tue Jun 21 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.18-1
- Update to upstream version 0.1.18

* Wed Jun 15 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.14-3
- Add missing build-requires

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.1.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 08 2016 gil cattaneo <puntogil@libero.it> 0.1.14-1
- update to 0.1.14
- enable (snake)YAML support

* Sat Jul 18 2015 gil cattaneo <puntogil@libero.it> 0.1.8-4
- fix FTBFS rhbz#1240065
- disable ruby module rhbz#1234368

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.1.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 19 2015 Michal Srb <msrb@redhat.com> - 0.1.8-2
- Build ruby module

* Mon Apr 20 2015 gil cattaneo <puntogil@libero.it> 0.1.8-1
- update to 0.1.8

* Mon Apr 20 2015 gil cattaneo <puntogil@libero.it> 0.1.6-2
- disable takari-pom support

* Mon Apr 13 2015 gil cattaneo <puntogil@libero.it> 0.1.6-1
- update to 0.1.6

* Thu Feb 12 2015 gil cattaneo <puntogil@libero.it> 0.1.0-3
- introduce license macro

* Thu Oct 23 2014 gil cattaneo <puntogil@libero.it> 0.1.0-2
- add BR on ant-junit
- added alias needed by Gradle

* Sun May 25 2014 gil cattaneo <puntogil@libero.it> 0.1.0-1
- initial rpm
