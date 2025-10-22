<class name="Player">
    <function name="attack">
        <print>{self.name} attacks {arg1} for {arg2} damage!</print>
    </function>
    <var name="name" value="'Jay Sandler'"/>
</class>

<var name="p" value="Player()"/>
<call name="p.attack('enemy', 5)"/>
<call name="Player().attack('boss', 15)"/>

:: If you add 'ignore-crf="true"' to the 'class' tag, it does not print the Class Registration Feedback.