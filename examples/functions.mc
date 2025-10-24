<function name="greet">
    <print>Hello from inside the function!</print>
</function>

<function name="countdown">
    <print>3...</print>
    <wait seconds="1"/>
    <print>2...</print>
    <wait seconds="1"/>
    <print>1...</print>
    <print>Go!</print>
</function>

<call name="greet"/>
<call name="countdown"/>
