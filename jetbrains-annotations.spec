%{?_javapackages_macros:%_javapackages_macros}

%define sname annotations

Summary:	Annotating source code for IntelliJ IDEA
Name:		jetbrains-annotations
Version:	15.0
Release:	0
License:	Apache Software License
Group:		Development/Java
URL:		http://www.jetbrains.org/
Source0:	https://repo1.maven.org/maven2/org/jetbrains/%{sname}/%{version}/%{sname}-%{version}-sources.jar
Source1:	https://repo1.maven.org/maven2/org/jetbrains/%{sname}/%{version}/%{sname}-%{version}.pom
#Source100:	%{name}.rpmlintrc
BuildArch:	noarch

BuildRequires:	maven-local

%description
A set of annotations used for code inspection support and code documentation.

%files -f .mfiles

#----------------------------------------------------------------------------

%package javadoc
Summary:	Javadoc for %{name}

%description javadoc
API documentation for %{name}.

%files javadoc -f .mfiles-javadoc

#----------------------------------------------------------------------------

%prep
%setup -q -T 0 -c %{sname}-%{version}
mkdir -p src/main/java/ src/test/java/

# sources
pushd src/main/java/
%jar -xf %{SOURCE0}
popd

# Delete all prebuild JARs and classes
find . -name "*.jar" -delete
find . -name "*.class" -delete

# Copy the pom.xml file in the right place
cp %{SOURCE1} pom.xml

# Remove unused plugin
%pom_remove_plugin :maven-antrun-plugin
%pom_remove_plugin :maven-gpg-plugin
%pom_remove_plugin :maven-source-plugin

# Bundle
%pom_xpath_replace "pom:project/pom:packaging" "<packaging>bundle</packaging>" .

# Add an OSGi compilant MANIFEST.MF
%pom_add_plugin org.apache.felix:maven-bundle-plugin "
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

# Fix jar name
%mvn_file :%{sname} %{name}-%{version} %{name}

%build
%mvn_build 

%install
%mvn_install

