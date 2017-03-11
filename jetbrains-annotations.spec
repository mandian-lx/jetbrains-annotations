%{?_javapackages_macros:%_javapackages_macros}

%global oname annotations
Name:          jetbrains-annotations
Version:       15.0
Release:       4
Summary:       IntelliJ IDEA Annotations
License:       ASL 2.0
Group:         Development/Java
URL:           http://www.jetbrains.org
Source0:       http://central.maven.org/maven2/org/jetbrains/annotations/%{version}/annotations-%{version}-sources.jar
Source1:       http://central.maven.org/maven2/org/jetbrains/annotations/%{version}/annotations-%{version}.pom
Source2:       http://www.apache.org/licenses/LICENSE-2.0.txt

BuildRequires: maven-local

BuildArch:     noarch

%description
A set of annotations used for code inspection support and code documentation.

%package javadoc
Summary:       Javadoc for %{name}
Group:         Development/Java

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -T -q -c

mkdir -p src/main/{java,resources}

(
  cd src/main/java
  %jar -xf %{SOURCE0}
  rm -rf META-INF
)

cp -p %{SOURCE1} pom.xml

%pom_remove_plugin :maven-antrun-plugin
%pom_remove_plugin :maven-gpg-plugin
%pom_remove_plugin :maven-javadoc-plugin
%pom_remove_plugin :maven-source-plugin

%pom_xpath_inject pom:properties "<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>"

cp -p %{SOURCE2} LICENSE.txt
sed -i 's/\r//' LICENSE.txt
chmod 644 LICENSE.txt

# Bundle
%pom_xpath_replace "pom:project/pom:packaging" "<packaging>bundle</packaging>" .

# Add an OSGi compilant MANIFEST.MF
%pom_add_plugin org.apache.felix:maven-bundle-plugin . "
<extensions>true</extensions>
<configuration>
	<supportedProjectTypes>
		<supportedProjectType>bundle</supportedProjectType>
		<supportedProjectType>jar</supportedProjectType>
	</supportedProjectTypes>
	<instructions>
		<Bundle-Name>\${project.artifactId}</Bundle-Name>
		<Bundle-Version>\${project.version}</Bundle-Version>
	</instructions>
</configuration>
<executions>
	<execution>
		<id>bundle-manifest</id>
		<phase>process-classes</phase>
		<goals>
			<goal>manifest</goal>
		</goals>
	</execution>
</executions>"

# Add the META-INF/INDEX.LIST (fix jar-not-indexed warning) and
# the META-INF/MANIFEST.MF to the jar archive
%pom_add_plugin :maven-jar-plugin . "
<executions>
	<execution>
		<phase>package</phase>
		<configuration>
			<archive>
				<manifestFile>\${project.build.outputDirectory}/META-INF/MANIFEST.MF</manifestFile>
				<manifest>
					<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
					<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
				</manifest>
				<index>true</index>
			</archive>
		</configuration>
		<goals>
			<goal>jar</goal>
		</goals>
	</execution>
</executions>"

%mvn_file org.jetbrains:%{oname} %{name}
%mvn_alias org.jetbrains:%{oname} com.intellij:%{oname}

%build

%mvn_build

%install
%mvn_install -X -- -r

%files -f .mfiles
%doc LICENSE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt

%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 15.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Jun 22 2016 gil cattaneo <puntogil@libero.it> 15.0-3
- regenerate build-requires

* Wed Apr 27 2016 gil cattaneo <puntogil@libero.it> 15.0-2
- review fixes

* Sun Mar 20 2016 gil cattaneo <puntogil@libero.it> 15.0-1
- initial rpm
