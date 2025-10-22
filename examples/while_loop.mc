<var>
    x: 0;
</var>

<while condition="{x} < 3">
    <print>Loop: {x}</print>
    <calc>{x} + 1</calc>
    <var name="x" value="{x} + 1" />
</while>

<print>While loop finished!</print>
